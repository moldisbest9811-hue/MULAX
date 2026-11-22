"""Best-effort local hardware and accelerator detection."""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass


@dataclass
class HardwareInfo:
    operating_system: str
    processor: str
    logical_cpu_threads: int
    physical_cpu_cores: int | None
    total_ram_gb: float | None
    available_ram_gb: float | None
    nvidia_gpu: str | None
    vram_gb: float | None
    cuda_available_to_torch: bool
    torch_version: str | None
    notes: list[str]

    def as_dict(self):
        return asdict(self)


def _ram_info():
    try:
        import psutil
        vm = psutil.virtual_memory()
        return round(vm.total / 1024**3, 1), round(vm.available / 1024**3, 1)
    except ImportError:
        return None, None


def _cpu_cores():
    try:
        import psutil
        return psutil.cpu_count(logical=False)
    except ImportError:
        return None


def _nvidia_info():
    executable = shutil.which("nvidia-smi")
    if not executable:
        return None, None
    try:
        result = subprocess.run(
            [executable, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5, check=True
        )
        first = result.stdout.strip().splitlines()[0]
        name, memory = [part.strip() for part in first.split(",", 1)]
        return name, round(float(memory) / 1024, 1)
    except (subprocess.SubprocessError, ValueError, IndexError):
        return None, None


def detect_hardware() -> HardwareInfo:
    notes = []
    total_ram, available_ram = _ram_info()
    if total_ram is None:
        notes.append("Install psutil for RAM totals and physical-core detection.")
    gpu_name, vram = _nvidia_info()
    if gpu_name is None:
        notes.append("nvidia-smi was not found or did not return a GPU. Check the NVIDIA driver.")
    torch_available = False
    torch_version = None
    try:
        import torch
        torch_version = torch.__version__
        torch_available = bool(torch.cuda.is_available())
        if torch.cuda.is_available():
            notes.append(f"PyTorch CUDA device: {torch.cuda.get_device_name(0)}")
        elif gpu_name:
            notes.append("NVIDIA GPU detected, but PyTorch CUDA is not available; llama.cpp may still use CUDA if built with it.")
    except ImportError:
        notes.append("PyTorch is not installed. Hardware detection still works; install it for CUDA checks and future training.")
    except Exception as exc:
        notes.append(f"PyTorch check returned: {exc}")

    return HardwareInfo(
        operating_system=f"{platform.system()} {platform.release()}",
        processor=platform.processor() or platform.machine(),
        logical_cpu_threads=os.cpu_count() or 1,
        physical_cpu_cores=_cpu_cores(),
        total_ram_gb=total_ram,
        available_ram_gb=available_ram,
        nvidia_gpu=gpu_name,
        vram_gb=vram,
        cuda_available_to_torch=torch_available,
        torch_version=torch_version,
        notes=notes,
    )


def recommended_gpu_layers(info: HardwareInfo) -> int:
    """Conservative starting point; user can override with MULAX_GPU_LAYERS."""
    if info.vram_gb is None:
        return 0
    if info.vram_gb < 6:
        return 8
    if info.vram_gb < 10:
        return 20
    if info.vram_gb < 14:
        return 28
    if info.vram_gb < 20:
        return 36
    return -1  # llama.cpp convention: attempt all layers

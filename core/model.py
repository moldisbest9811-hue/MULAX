"""Optional local GGUF model adapter using llama-cpp-python."""
from __future__ import annotations

from config import (
    CONTEXT_SIZE, GPU_LAYERS_OVERRIDE, MAX_TOKENS, MODEL_PATH, TEMPERATURE
)
from core.hardware import detect_hardware, recommended_gpu_layers


class LocalLanguageModel:
    def __init__(self):
        self.model = None
        self.error = None
        self.gpu_layers = 0

    @property
    def available(self) -> bool:
        return self.model is not None

    def load(self) -> bool:
        if not MODEL_PATH.is_file():
            self.error = (
                f"No GGUF model file found at: {MODEL_PATH}\n"
                "See README.md for setup instructions."
            )
            return False

        try:
            from llama_cpp import Llama
        except ImportError:
            self.error = "llama-cpp-python is not installed. Follow README.md."
            return False

        info = detect_hardware()
        threads = max(1, (info.physical_cpu_cores or info.logical_cpu_threads) - 1)
        if GPU_LAYERS_OVERRIDE is not None:
            try:
                self.gpu_layers = int(GPU_LAYERS_OVERRIDE)
            except ValueError:
                self.error = "MULAX_GPU_LAYERS must be an integer."
                return False
        else:
            self.gpu_layers = recommended_gpu_layers(info)

        try:
            self.model = Llama(
                model_path=str(MODEL_PATH),
                n_ctx=CONTEXT_SIZE,
                n_threads=threads,
                n_gpu_layers=self.gpu_layers,
                n_batch=256,
                use_mmap=True,
                verbose=False,
            )
            return True
        except Exception as exc:
            self.error = (
                f"Could not load model with {self.gpu_layers} GPU layers: {exc}\n"
                "Try reducing MULAX_GPU_LAYERS in your environment."
            )
            self.model = None
            return False

    def generate(self, prompt: str, max_tokens: int = MAX_TOKENS) -> str:
        if not self.model:
            raise RuntimeError("The local language model is not loaded.")
        result = self.model.create_chat_completion(
            messages=[
                {"role": "system", "content": (
                    "You are MULAX, a friendly, intelligent, curious, conversational, "
                    "occasionally humorous, creative and analytical local AI assistant. "
                    "Adapt your tone to the user's situation. Be honest about uncertainty. "
                    "Do not claim to have browsed the internet unless a search result was provided."
                )},
                {"role": "user", "content": prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=max_tokens,
        )
        return result["choices"][0]["message"]["content"].strip()

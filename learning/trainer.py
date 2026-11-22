"""Training readiness checks; no training is performed in this starter release."""


def training_status() -> str:
    try:
        import torch
        if torch.cuda.is_available():
            return f"PyTorch {torch.__version__}; CUDA ready on {torch.cuda.get_device_name(0)}. No model training job is configured yet."
        return f"PyTorch {torch.__version__} installed; CUDA unavailable. No model training job is configured yet."
    except ImportError:
        return "PyTorch is not installed. Training support is planned after model integration."

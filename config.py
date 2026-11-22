import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "mulax_memory.sqlite3"
MODEL_PATH = Path(os.environ.get("MULAX_MODEL_PATH", PROJECT_ROOT / "models" / "model.gguf"))
MODEL_PATH = MODEL_PATH.expanduser()

APP_NAME = "MULAX"
VERSION = "0.2.0"

# Hybrid inference settings. Set MULAX_GPU_LAYERS to override automatic selection.
GPU_LAYERS_OVERRIDE = os.environ.get("MULAX_GPU_LAYERS")
CONTEXT_SIZE = int(os.environ.get("MULAX_CONTEXT_SIZE", "4096"))
TEMPERATURE = float(os.environ.get("MULAX_TEMPERATURE", "0.75"))
MAX_TOKENS = int(os.environ.get("MULAX_MAX_TOKENS", "512"))

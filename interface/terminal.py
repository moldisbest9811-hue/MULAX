from config import APP_NAME, VERSION, DATABASE_PATH, MODEL_PATH
from core.brain import MULAXBrain
from core.hardware import detect_hardware
from core.model import LocalLanguageModel
from learning.trainer import training_status
from memory.long_term import MemoryStore
from research.web_search import search_web

HELP = """
Commands:
  /help                 Show commands
  /hardware             Detect CPU, RAM, NVIDIA GPU and CUDA
  /model                Show local model status
  /load                 Load the configured GGUF model
  /remember <note>      Save a note locally
  /memory               List saved notes
  /forget <id>          Delete a saved note
  /search <query>       Search the web (requires internet + ddgs package)
  /train                Show PyTorch/training readiness
  /quit                 Exit MULAX

Chat normally, or try: calculate 12 * (4 + 3)
"""

def show_hardware():
    info = detect_hardware()
    print(f"OS: {info.operating_system}")
    print(f"CPU: {info.processor}")
    print(f"CPU threads: {info.logical_cpu_threads}; physical cores: {info.physical_cpu_cores or 'unknown'}")
    print(f"RAM: {info.total_ram_gb if info.total_ram_gb is not None else 'unknown'} GB total; "
          f"{info.available_ram_gb if info.available_ram_gb is not None else 'unknown'} GB available")
    print(f"NVIDIA GPU: {info.nvidia_gpu or 'not detected'}")
    print(f"VRAM: {info.vram_gb if info.vram_gb is not None else 'unknown'} GB")
    print(f"PyTorch CUDA: {'available' if info.cuda_available_to_torch else 'not available'}")
    for note in info.notes:
        print(f"Note: {note}")

def run_terminal():
    memory = MemoryStore(DATABASE_PATH)
    model = LocalLanguageModel()
    brain = MULAXBrain(memory, model)

    print(f"\n{APP_NAME} v{VERSION}")
    print("Local-first hybrid AI foundation. Type /help for commands.")
    print(f"Model path: {MODEL_PATH}")
    print("No model is loaded automatically. Use /load after placing a GGUF file there.\n")

    try:
        while True:
            try:
                message = input("You > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nMULAX > Goodbye.")
                break
            if not message:
                continue
            if message == "/quit":
                print("MULAX > Goodbye.")
                break
            elif message == "/help":
                print(HELP)
            elif message == "/hardware":
                show_hardware()
            elif message == "/model":
                if model.available:
                    print(f"MULAX > Model loaded. GPU layers: {model.gpu_layers}")
                else:
                    print(f"MULAX > Model not loaded. {model.error or 'Use /load to attempt loading.'}")
            elif message == "/load":
                print("MULAX > Loading local model. This may take a while...")
                if model.load():
                    print(f"MULAX > Model loaded. GPU layers: {model.gpu_layers} (-1 means all layers requested).")
                else:
                    print(f"MULAX > {model.error}")
            elif message.startswith("/remember "):
                note = message[len("/remember "):].strip()
                if note:
                    memory.remember(note)
                    print("MULAX > Saved to local memory.")
                else:
                    print("MULAX > Add a note after /remember.")
            elif message == "/memory":
                notes = memory.list_memories()
                if not notes:
                    print("MULAX > Your memory is empty.")
                else:
                    for memory_id, note in notes:
                        print(f"  [{memory_id}] {note}")
            elif message.startswith("/forget "):
                try:
                    memory_id = int(message[len("/forget "):].strip())
                    print("MULAX > Memory deleted." if memory.forget(memory_id)
                          else "MULAX > No memory with that ID.")
                except ValueError:
                    print("MULAX > Usage: /forget <id>")
            elif message.startswith("/search "):
                query = message[len("/search "):].strip()
                if not query:
                    print("MULAX > Usage: /search <query>")
                    continue
                try:
                    results = search_web(query)
                    if not results:
                        print("MULAX > No results returned.")
                    for index, result in enumerate(results, 1):
                        print(f"\n[{index}] {result['title']}\n{result['url']}\n{result['snippet']}")
                except Exception as exc:
                    print(f"MULAX > Search failed: {exc}")
            elif message == "/train":
                print("MULAX > " + training_status())
            else:
                print("MULAX > " + brain.respond(message))
    finally:
        memory.close()

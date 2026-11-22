# MULAX v0.2 — Local-first hybrid foundation

This release adds hardware detection, optional GGUF model inference through
`llama-cpp-python`, conservative CPU/GPU layer offload, local memory retrieval,
a personality system prompt, and explicit user-triggered web search.

## Run

```powershell
py main.py
```

No third-party package is required just to start the terminal. For hardware
reporting and web search, install:

```powershell
py -m pip install -r requirements.txt
```

## Hardware detection

Inside MULAX, run:

```text
/hardware
```

It reports CPU threads/cores, RAM, NVIDIA GPU, VRAM and whether PyTorch sees CUDA.
`nvidia-smi` must be available for NVIDIA model/VRAM detection.

## Add a local language model

1. Create a `models` folder in the MULAX project directory.
2. Obtain a compatible **GGUF instruct/chat model** from a reputable model publisher.
3. Place the `.gguf` file in `MULAX\models\model.gguf`, or set `MULAX_MODEL_PATH`
   to its full path.
4. Install a compatible `llama-cpp-python` build.
5. Start MULAX and run `/load`.

For an 8 GB VRAM GPU, start with a small quantized instruct model (roughly 3B–4B
parameters, Q4 quantization) and a 4K context. A 7B Q4 model may be possible with
partial GPU offload, but memory use varies by architecture, context length and
runtime overhead. Keep other GPU-heavy applications closed during initial tests.

### CUDA note

A plain `pip install llama-cpp-python` may install a CPU-only build. GPU acceleration
requires a CUDA-enabled build compatible with your installed NVIDIA driver and
CUDA toolchain. Follow the current official installation instructions:
https://github.com/abetlen/llama-cpp-python

PyTorch CUDA availability and llama.cpp CUDA availability are separate checks.
A GPU appearing in `/hardware` does not prove the inference backend has CUDA enabled.

### CPU/GPU hybrid behavior

MULAX uses llama.cpp's `n_gpu_layers` setting to offload a portion of model layers
to the GPU while the remaining layers run on the CPU. The default layer count is
conservative and based on detected VRAM. This is a starting heuristic, not a
guarantee of optimal performance or memory fit.

Override it in PowerShell for the current terminal session:

```powershell
$env:MULAX_GPU_LAYERS="12"
py main.py
```

Use `0` for CPU-only. Increase gradually if VRAM remains available. Use `-1`
to request all layers on the GPU, but this can fail if the model and context do
not fit in VRAM. You can also adjust context:

```powershell
$env:MULAX_CONTEXT_SIZE="2048"
py main.py
```

## Internet research

Web search is opt-in and user-triggered:

```text
/search latest Python documentation
```

Search results are displayed with their URLs and snippets. MULAX does not silently
browse in the background, and search results should be checked before relying on them.
The search feature requires the `ddgs` package and an internet connection.

## Memory

- `/remember <note>` stores a note in `data\mulax_memory.sqlite3`.
- `/memory` lists saved notes.
- `/forget <id>` deletes one saved note.

Conversation memory is currently a lightweight keyword-overlap retrieval system,
not semantic/vector memory. The model receives matching notes and recent turns
as prompt context.

## Current limitations

- This is an early engineering foundation, not an independently trained foundation model.
- The model must be obtained separately; no model weights are bundled.
- No automatic online learning or model-weight updates occur.
- The current reasoning module includes a restricted arithmetic evaluator.
- Internet search is explicit, not autonomous.
- CUDA support depends on installing a CUDA-enabled llama.cpp backend.

## Troubleshooting

- `No GGUF model file found`: put a model at `models\model.gguf` or set `MULAX_MODEL_PATH`.
- `llama-cpp-python is not installed`: install the package in the same Python environment.
- CUDA/GPU initialization failure: try `MULAX_GPU_LAYERS=0` first, then a small positive layer count.
- Out of memory: reduce GPU layers and context size; try a smaller quantized model.

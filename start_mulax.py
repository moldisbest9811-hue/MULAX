from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main() -> int:
    print("Starting MULAX...")
    try:
        from updater import run_update
        run_update()
    except Exception as exc:
        print(f"[MULAX updater] Update check skipped: {exc}")
        print("[MULAX updater] Continuing with the installed version.")

    main_file = ROOT / "main.py"
    if not main_file.exists():
        print("ERROR: main.py was not found in the MULAX folder.")
        input("Press Enter to close...")
        return 1
    return subprocess.call([sys.executable, str(main_file)], cwd=str(ROOT))

if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "updater_config.json"
USER_AGENT = "MULAX-Updater/1.0"
MAX_DOWNLOAD_BYTES = 250 * 1024 * 1024

PROTECTED_TOP_LEVEL = {"memory", "models", "data", "backups", ".git", "__pycache__"}
PROTECTED_FILES = {"updater_config.json", "updater.py", "start_mulax.py"}

def log(message: str) -> None:
    print(f"[MULAX updater] {message}")

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("updater_config.json is missing.")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

def github_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))

def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    total = 0
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_DOWNLOAD_BYTES:
                raise RuntimeError("Update package exceeds the 250 MB safety limit.")
            out.write(chunk)

def safe_relative_path(value: str) -> Path:
    posix = PurePosixPath(value)
    if posix.is_absolute() or not posix.parts or any(part in ("..", "") for part in posix.parts):
        raise ValueError(f"Unsafe update path rejected: {value}")
    if ":" in posix.parts[0] or "\\" in value:
        raise ValueError(f"Unsafe update path rejected: {value}")
    relative = Path(*posix.parts)
    if relative.parts[0].lower() in PROTECTED_TOP_LEVEL:
        raise ValueError(f"Update attempted to replace protected folder: {value}")
    if relative.name in PROTECTED_FILES:
        raise ValueError(f"Update attempted to replace protected updater file: {value}")
    return relative

def run_update() -> bool:
    config = load_config()
    owner = str(config.get("github_owner", "")).strip()
    repo = str(config.get("github_repo", "")).strip()
    current_version = str(config.get("version", "0.2.0")).strip()
    asset_name = str(config.get("asset_name", "mulax-update.zip")).strip()
    if not owner or not repo:
        log("GitHub owner/repository is not configured.")
        return False

    try:
        release = github_json(f"https://api.github.com/repos/{owner}/{repo}/releases/latest")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            log("No GitHub release found yet. MULAX will start normally.")
            return False
        raise

    latest_version = str(release.get("tag_name", "")).lstrip("v")
    if not latest_version:
        log("Latest GitHub release has no version tag; skipping.")
        return False
    if latest_version == current_version:
        log(f"MULAX is up to date (v{current_version}).")
        return False

    asset = next((item for item in release.get("assets", []) if item.get("name") == asset_name), None)
    if not asset:
        log(f"Release v{latest_version} has no {asset_name} asset; skipping.")
        return False

    log(f"Update found: v{current_version} -> v{latest_version}")
    with tempfile.TemporaryDirectory(prefix="mulax-update-") as temp_name:
        temp = Path(temp_name)
        archive = temp / asset_name
        download(asset["browser_download_url"], archive)
        with zipfile.ZipFile(archive, "r") as package:
            names = package.namelist()
            if "manifest.json" not in names:
                raise RuntimeError("Update package has no manifest.json.")
            manifest = json.loads(package.read("manifest.json").decode("utf-8"))
            files = manifest.get("files")
            if not isinstance(files, dict) or not files:
                raise RuntimeError("Update manifest has no file hash list.")
            staged = {}
            for raw_path, expected_hash in files.items():
                relative = safe_relative_path(raw_path)
                if raw_path not in names:
                    raise RuntimeError(f"Manifest file missing from package: {raw_path}")
                content = package.read(raw_path)
                if hashlib.sha256(content).hexdigest().lower() != str(expected_hash).lower():
                    raise RuntimeError(f"SHA-256 verification failed for {raw_path}")
                staged_path = temp / "staged" / relative
                staged_path.parent.mkdir(parents=True, exist_ok=True)
                staged_path.write_bytes(content)
                staged[relative] = staged_path

        backup_root = ROOT / "backups" / ("update-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
        replaced = []
        try:
            for relative, staged_path in staged.items():
                target = ROOT / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                old_copy = None
                if target.exists():
                    old_copy = backup_root / relative
                    old_copy.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, old_copy)
                replaced.append((target, old_copy))
                shutil.copy2(staged_path, target)
            config["version"] = latest_version
            CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
            log(f"Successfully updated MULAX to v{latest_version}.")
            log(f"Backup saved at: {backup_root}")
            return True
        except Exception:
            log("Update failed. Restoring files from backup...")
            for target, old_copy in reversed(replaced):
                try:
                    if old_copy and old_copy.exists():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(old_copy, target)
                    elif target.exists():
                        target.unlink()
                except OSError:
                    pass
            raise

if __name__ == "__main__":
    try:
        run_update()
    except Exception as exc:
        log(f"Update check failed safely: {exc}")
        log("MULAX can still start with its existing files.")

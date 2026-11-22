# MULAX Automatic Updater (one-time setup)

This adds a startup updater to an existing MULAX v0.2 folder. It uses only Python's
standard library; no extra pip packages are needed.

## 1. Install once

1. Extract this ZIP.
2. Copy `updater.py`, `start_mulax.py`, and `updater_config.json` into the same
   folder as your existing `main.py`.
3. Open `updater_config.json` and replace `YOUR_GITHUB_USERNAME` with your GitHub
   username. The repository name is `MULAX` by default; change it if yours differs.
4. Start MULAX with:
   `py start_mulax.py`

Use `start_mulax.py` from now on instead of `py main.py`.

## 2. Publish a release when you make an update

Create a GitHub repository, then publish a GitHub Release with a tag such as
`v0.3.0`. Attach an asset named exactly `mulax-update.zip`.

The asset must contain:
- `manifest.json` at the ZIP root
- each updated file at its project-relative path

Example package layout:
```
manifest.json
main.py
core/brain.py
core/model.py
```

Example `manifest.json`:
```json
{
  "files": {
    "main.py": "SHA256_HEX_FOR_MAIN_PY",
    "core/brain.py": "SHA256_HEX_FOR_BRAIN_PY"
  }
}
```

The SHA-256 values must be the actual SHA-256 hashes of the exact file bytes.
Only list files that should be replaced. The updater downloads the latest release,
verifies every listed file, backs up replaced files, then applies the update.

## Safety behavior

- `memory/`, `models/`, `data/`, `backups/`, `.git/`, and Python cache folders are
  protected from updates.
- `updater.py`, `start_mulax.py`, and `updater_config.json` are protected.
- Paths are checked to prevent ZIP path traversal.
- Every listed file is SHA-256 verified before anything is installed.
- Existing files are backed up under `backups/`.
- If applying files fails, the updater attempts to restore the previous files.
- If GitHub is unavailable or no release exists, MULAX starts using its current files.

## Important

This starter package does not create or publish your GitHub repository. Automatic
updates become active after you create the repository and publish a correctly
formatted GitHub Release. For a private repository, a GitHub token and secure token
storage would be needed; this starter is intended for a public repository.

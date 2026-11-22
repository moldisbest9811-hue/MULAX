# MULAX updater installation

Copy `updater.py`, `start_mulax.py`, and `updater_config.json` beside `main.py` in your local MULAX folder. Start the app with `py start_mulax.py`.

The updater checks the latest release of https://github.com/moldisbest9811-hue/MULAX and looks for an asset named `mulax-update.zip`. Releases are generated automatically when a version tag beginning with `v` is pushed.

User data folders (`memory`, `models`, `data`, `backups`) and updater files are excluded from automatic replacement. Do not commit personal data, model weights, API keys, or access tokens.

This repository currently contains the updater infrastructure. The MULAX application source must still be uploaded to the repository before a complete application release can be built.

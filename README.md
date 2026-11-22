# MULAX

MULAX is a local-first hybrid AI project.

## Automatic updates

The desktop updater checks the latest GitHub Release in this repository. Release assets must be named `mulax-update.zip` and contain a `manifest.json` at the ZIP root. The manifest maps each included project-relative file path to its SHA-256 hash.

### Publishing an update

1. Push the updated MULAX source files to the `main` branch.
2. Create and push a version tag, for example: `git tag v0.3.0 && git push origin v0.3.0`.
3. The GitHub Actions workflow builds `mulax-update.zip`, creates the hash manifest, and publishes the asset on a GitHub Release.

The updater deliberately excludes user data and local configuration such as `memory/`, `models/`, `data/`, `backups/`, `.git/`, `updater_config.json`, and the updater launcher files.

## Important

This repository starts as the update channel. The MULAX application source files still need to be pushed from your local `MULAX_v0.2` folder before a release can contain a complete application update. Never commit private tokens, personal memory databases, or model files.

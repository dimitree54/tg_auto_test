# Release Workflow

This document describes how to release a new version of `tg-auto-test` to PyPI.

## Overview

Releases are automated via GitHub Actions (`.github/workflows/release.yml`). The workflow triggers on tag pushes matching `v*`, builds the package, and publishes to PyPI using `twine`.

## Prerequisites

- Push access to the `main` branch
- `gh` CLI authenticated with the repository
- All quality gates passing (`make check`)

## Pre-release checklist

1. **All changes merged to `main`** — no pending PRs for this release.
2. **`make check` passes 100%** — formatting, linting, dead code, duplicates, and tests.
3. **`uv run python -m build` succeeds** — the package builds cleanly.
4. **Commit messages are clean** — release commits follow the `[RELEASE] Bump version to X.Y.Z: summary` convention.

## Release steps

### 1. Bump the version

Edit `pyproject.toml` and update the `version` field:

```toml
[project]
version = "X.Y.Z"
```

### 2. Commit and push

```bash
git add pyproject.toml
git commit -m "[RELEASE] Bump version to X.Y.Z: brief description of changes"
git push origin main
```

### 3. Create a local tag

```bash
git tag vX.Y.Z
```

**Do NOT push this tag with `git push --tags`** — pushing tags via git does not reliably trigger the `on: push: tags` GitHub Actions workflow.

### 4. Create the tag via GitHub API

This is the only method that reliably triggers the release workflow:

```bash
gh api repos/{owner}/{repo}/git/refs \
  -f ref=refs/tags/vX.Y.Z \
  -f sha=$(git rev-parse vX.Y.Z)
```

### 5. Verify the release workflow started

```bash
gh run list --workflow=release.yml --limit 1
```

Wait for it to complete successfully. If it fails, inspect the logs:

```bash
gh run view <RUN_ID> --log-failed
```

### 6. Create the GitHub release

Once the workflow succeeds, create the release pointing to the existing tag:

```bash
gh release create vX.Y.Z --title "vX.Y.Z" --verify-tag --notes "Release notes here..."
```

Use `--verify-tag` to reuse the existing tag rather than creating a new one.

**Release notes format** — follow the established pattern:

```markdown
## Bug fix / Feature / Refactor

- **summary of change (fixes #N)**
  - Detail 1
  - Detail 2

Test suite: N1 -> N2 tests
```

### 7. Verify on PyPI

```bash
curl -s https://pypi.org/pypi/tg-auto-test/json | python3 -c \
  "import sys,json; print(json.load(sys.stdin)['info']['version'])"
```

## Versioning policy

This project uses [semantic versioning](https://semver.org/):

- **Patch** (`X.Y.Z+1`) — bug fixes, test additions, doc updates
- **Minor** (`X.Y+1.0`) — new features, new method implementations, backward-compatible API additions
- **Major** (`X+1.0.0`) — breaking API changes (rare, since we mirror Telethon's interface)

## Commit message convention

Release commits follow this format:

```
[RELEASE] Bump version to X.Y.Z: brief summary of what changed
```

Examples from this repo:
- `[RELEASE] Bump version to 1.3.16: QA hardening — return-type conformance, behavioral parity, and stub classification tests`
- `[RELEASE] Bump version to 1.3.12: stream SSE events concurrently with handler execution (fixes #23)`

## Troubleshooting

### Release workflow did not trigger

The `on: push: tags` trigger only works when the tag is created via the GitHub Git refs API. If you pushed the tag with `git push`, delete it and recreate:

```bash
# Delete the remote tag
gh api repos/{owner}/{repo}/git/refs/tags/vX.Y.Z -X DELETE

# Recreate via API
gh api repos/{owner}/{repo}/git/refs \
  -f ref=refs/tags/vX.Y.Z \
  -f sha=$(git rev-parse vX.Y.Z)
```

### PyPI upload failed

Check that the `PYPI_API_TOKEN` secret is configured in the `release` environment on GitHub. The workflow uses `twine upload` with token authentication.

### Build fails locally

```bash
uv sync --dev
uv run python -m build
uv run twine check dist/*
```

Fix any issues before attempting a release.

## CI pipeline

Every push to `main` and every PR runs the full quality gate via `.github/workflows/ci.yml`:

1. `ruff format --check` + `ruff check`
2. `pylint` (200-line module limit)
3. `vulture` (dead code detection)
4. `jscpd` (duplicate code detection)
5. `pytest -n auto` (full test suite)
6. `python -m build` (package build)

Tested on Python 3.12 and 3.13. **A release should never be cut unless CI is green on `main`.**

# TASK_05 — Publish tg-auto-test 0.5.0 and update proto_tg_bot

**Repo:** Both `/Users/yid/source/tg_auto_test` and `/Users/yid/source/proto_tg_bot`
**Dependencies:** TASK_01, TASK_02, TASK_03, TASK_04

## Description

Bump `tg-auto-test` to version 0.5.0, publish it, then update `proto_tg_bot` to use the new version and verify all tests pass — including the poll serverless tests that were `xfail` in TASK_01.

### Step 1 — Final validation in tg-auto-test

Run `make check` in `tg-auto-test` one last time to confirm everything from TASK_02–04 is green.

### Step 2 — Bump version

In `tg_auto_test/pyproject.toml`, change:
```
version = "0.4.0"
```
to:
```
version = "0.5.0"
```

### Step 3 — Tag and publish

Create a git tag `v0.5.0`. If CI publishes on tag push, just push the tag. Otherwise, build and publish manually:
```bash
uv run python -m build
uv run twine upload dist/tg_auto_test-0.5.0*
```

### Step 4 — Update proto_tg_bot dependency

In `proto_tg_bot/pyproject.toml`, change:
```
"tg-auto-test[demo]==0.4.0",
```
to:
```
"tg-auto-test[demo]==0.5.0",
```

Then run `uv lock` and `uv sync` to update the lock file.

### Step 5 — Remove xfail markers

In the poll test files created in TASK_01 (`tests/integration/test_poll.py`, `tests/e2e/test_bot_e2e.py` or `test_poll_e2e.py`), remove the `pytest.mark.xfail` markers that were added because tg-auto-test didn't support polls yet.

### Step 6 — Verify all green

Run `make check` in `proto_tg_bot`. All tests — including poll integration and e2e-serverless tests — must pass.

## Files to modify

| File | Repo | Action |
|------|------|--------|
| `pyproject.toml` | tg-auto-test | Bump version to `0.5.0` |
| `pyproject.toml` | proto_tg_bot | Update dependency to `tg-auto-test[demo]==0.5.0` |
| `uv.lock` | proto_tg_bot | Regenerate with `uv lock` |
| `tests/integration/test_poll.py` | proto_tg_bot | Remove `xfail` markers |
| `tests/e2e/test_bot_e2e.py` (or `test_poll_e2e.py`) | proto_tg_bot | Remove `xfail` markers |

## Acceptance Criteria

1. `tg-auto-test` version is `0.5.0` in `pyproject.toml`.
2. Git tag `v0.5.0` exists (or is ready to push).
3. `proto_tg_bot` depends on `tg-auto-test[demo]==0.5.0`.
4. No `xfail` markers remain on poll tests in proto_tg_bot.
5. `make check` in `tg-auto-test` is 100% green.
6. `make check` in `proto_tg_bot` is 100% green — all poll tests pass.

## Risks / Notes

- If publishing to PyPI, ensure the package builds cleanly first (`uv run python -m build`). Check that the `tg_auto_test/demo_ui/server/static/ui/*` assets are included (they're listed in `pyproject.toml` `package-data`).
- If the library is installed from a local path during development (e.g., `pip install -e ../tg_auto_test`), the version bump still matters for the lock file and for documenting the release.
- The `uv lock` step in proto_tg_bot may require the new version to be published (or use a path dependency temporarily). Coordinate accordingly.
- If any poll tests in proto_tg_bot fail after removing `xfail`, debug and fix before considering this task done — do not re-add `xfail`.

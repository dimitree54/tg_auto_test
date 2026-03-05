---
name: reproduce-fix-release
description: Pipeline of TDD bug fixing
---

1. Ask "reproduce-bug" subagent to reproduce the bug. Note: do not use "reproduce-bug" as a skill, but strictly as a subagent.
2. Make sure that "reproduce-bug" created a failing test. Note: do not write tests yourself. Only the "reproduce-bug" subagent is allowed to write tests.
3. Read repo docs and contribution guides
4. Fix the bug (following repo docs and contribution guides). Note: you are making not a hot-fix but a proper fix. Investigate the root cause of the bug. If some refactoring is needed for a proper fix - do it. Only a proper fix of the root cause is allowed. No hot-fixes, no hiding errors, no fallbacks. Only proper fix!
5. Make sure that the reproducing test became green
6. Explore all repo docs and contribution guides. Make sure that your fix is fully compliant. If needed, update docs to be up-to-date.
7. Create a GitHub release with the fix. Follow the release procedure below.

## Release procedure

The repo has a GitHub Actions workflow (`.github/workflows/release.yml`) that publishes to PyPI on tag push (`on: push: tags: ["v*"]`).

**Critical**: Neither `gh release create` nor `git push origin <tag>` reliably trigger `on: push: tags` workflows. The only method that works every time is creating the tag via the GitHub Git refs API.

Steps:

1. Bump the version in `pyproject.toml`.
2. Commit and push to `main`.
3. Create a local tag (but do NOT push it with git — it won't reliably trigger the workflow):
   ```bash
   git tag v<VERSION>
   ```
4. Create the tag on GitHub via the Git refs API:
   ```bash
   gh api repos/{owner}/{repo}/git/refs \
     -f ref=refs/tags/v<VERSION> \
     -f sha=$(git rev-parse v<VERSION>)
   ```
5. Wait ~30 seconds, then verify the Release workflow started and succeeded:
   ```bash
   gh run list --workflow=release.yml --limit 1
   ```
6. Once the Release workflow succeeds, create the GitHub release pointing to the existing tag:
   ```bash
   gh release create v<VERSION> --title "v<VERSION>" --verify-tag --notes "..."
   ```
   Use `--verify-tag` so it reuses the existing tag rather than creating a new one.
7. Verify the package is live on PyPI:
   ```bash
   curl -s https://pypi.org/pypi/<package>/json | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"
   ```

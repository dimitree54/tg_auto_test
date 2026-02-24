# Contributing to tg-auto-test

Thank you for your interest in contributing to tg-auto-test!

## Prerequisites

**Required tools:**
- Python 3.12+
- `uv` package manager ([installation guide](https://docs.astral.sh/uv/))
- Node.js (for jscpd duplicate detection)

## Development setup

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd tg-auto-test
   uv sync --dev
   ```

2. **Verify setup:**
   ```bash
   make check
   ```
   This must pass 100% before you can contribute.

## Development workflow

**All Python execution must go through `uv`:**
```bash
# Run tests
uv run pytest

# Run linters
uv run ruff check
uv run pylint tg_auto_test/

# Build package
uv run python -m build
```

**Quality gates:**
- Run `make check` before committing — it must pass completely
- No test skipping allowed
- No unreasonable linter suppressions
- All code must follow the project's style conventions

## Code style & standards

**Enforced by tooling:**
- Code formatting and linting enforced by ruff
- Type checking enforced by pylint
- Unused code detection with vulture
- Duplicate code detection with jscpd

**File size limits:**
- Maximum 200 lines per module (enforced by linter)
- When approaching the limit, decompose the module logically
- Never compact code or reformat to fit — always decompose

**Architecture principles:**
- Single Responsibility Principle for all modules/functions
- Fail-fast design — no silent fallbacks or defaults
- No legacy code — remove unused functionality completely

## Secrets management

**No `.env` files:**
This project uses Doppler for secrets management. Never commit:
- `.env` files
- `.env.template` files  
- Hardcoded API keys or tokens
- Any credentials in code or documentation

**Environment variables:**
See `docs/ENV_VARS.md` for documented environment variables.

## Testing guidelines

**Test requirements:**
- Prefer end-to-end and integration tests over unit tests
- Avoid excessive mocking — use real integrations when possible
- All tests must be deterministic and pass consistently
- Test coverage should be comprehensive, not just passing

**Running tests:**
```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/unit/test_serverless_client_text.py

# With coverage
uv run pytest --cov=tg_auto_test
```

## Pull request process

1. **Before coding:**
   - Open an issue to discuss significant changes
   - Check existing issues and PRs for related work

2. **Development:**
   - Create a feature branch from main
   - Make focused, atomic commits with clear messages
   - Run `make check` frequently during development

3. **Before submitting:**
   - Ensure `make check` passes 100%
   - Add tests for new functionality
   - Update documentation if needed
   - Verify no `proto_tg_bot` references exist in your changes

4. **Pull request:**
   - Use a clear title and description
   - Reference related issues
   - Include testing instructions if applicable

## Common gotchas

**Linter strictness:**
- The linter is intentionally strict — do not loosen it
- Fix linter issues rather than suppressing them
- File size limits are enforced — decompose large files

**Framework compatibility:**
- This library targets python-telegram-bot specifically
- Changes should maintain compatibility with PTB's interfaces
- Consider extension points for other frameworks

**Telethon compatibility:**
- Test interfaces MUST match Telethon's public signatures exactly (not 'where possible')
- Use `inspect` module conformance tests to verify interface alignment
- Unimplemented Telethon features raise `NotImplementedError`, never silent no-ops
- Extra `_`-prefixed methods are allowed for test infrastructure

## Getting help

- Open an issue for bugs or feature requests
- Use GitHub Discussions for questions and design discussions
- Check existing issues before creating new ones
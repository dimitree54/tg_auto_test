# Environment Variables

This document lists all environment variables used by `tg-auto-test`.

## Production environment variables

### PYPI_API_TOKEN

**Purpose:** PyPI publish token for automated package releases

**Usage:** Used only in CI release workflow for publishing packages to PyPI

**Management:** Managed via Doppler secrets management

**Local development:** Not needed for local development or testing

**Security note:** Never commit this token to version control. It is automatically injected by the CI system during release builds.

## Development environment

**No `.env` files:** This project uses Doppler for secrets management. We explicitly do not use:
- `.env` files
- `.env.template` files
- `python-dotenv` or `load_dotenv()`

**Local setup:** For local development, no environment variables are required. All functionality works out of the box with `uv sync --dev`.

## CI/CD environment variables

The CI system automatically provides the following:
- `PYPI_API_TOKEN` for package publishing
- Standard GitHub Actions environment variables
- Node.js environment for jscpd duplicate detection

## Adding new environment variables

If you need to add a new environment variable:

1. **Document it here** with purpose, usage, and management details
2. **Add it to Doppler** if it contains sensitive information
3. **Update CI configuration** if needed for automated workflows
4. **Never use `.env` files** — this project policy prohibits them

## Troubleshooting

**Missing environment variables:**
- Check Doppler configuration for production secrets
- Verify CI system has necessary access permissions
- Local development should not require any environment variables

**Permission errors:**
- Ensure proper access to Doppler projects
- Verify CI system service account permissions
- Contact maintainers for access issues
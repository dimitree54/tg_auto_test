# Security Policy

## Overview

`tg-auto-test` is a testing library designed for local development and CI environments. It does not process user data or make network connections to external services.

## Security model

**No network communication:**
- All Bot API calls are simulated in-memory
- No connections to real Telegram servers
- No external HTTP requests or data transmission

**No user data processing:**
- Library operates with synthetic test data only
- No collection, storage, or transmission of personal information
- Test scenarios use mock user profiles and content

## Reporting security issues

If you discover a security vulnerability in `tg-auto-test`, please report it through one of these channels:

1. **GitHub Issues:** Open a public issue for non-sensitive security concerns
2. **Email:** Contact the maintainers directly for sensitive security issues

**Please include:**
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix if available

## Response process

1. **Acknowledgment:** We will acknowledge receipt within 48 hours
2. **Investigation:** Security issues will be investigated promptly
3. **Resolution:** Fixes will be released as soon as possible
4. **Disclosure:** Public disclosure will follow responsible disclosure practices

## Security best practices

**For library users:**
- Use `tg-auto-test` only in development and testing environments
- Do not use production credentials or real user data in tests
- Keep your testing environment isolated from production systems
- Regularly update to the latest version for security fixes

**For contributors:**
- Follow secure coding practices
- Avoid hardcoding any credentials or sensitive data
- Use Doppler for any required secrets management
- Report security concerns during code review

## Out of scope

The following are considered out of scope for security reports:
- Issues in third-party dependencies (report to upstream projects)
- General Python or system-level security issues
- Issues requiring physical access to development machines
- Social engineering attacks against project contributors
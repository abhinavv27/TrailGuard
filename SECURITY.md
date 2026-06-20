# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.x (dev) | ✅ (active development) |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in TrailGuard AI, please follow these steps:

### DO NOT
- Do **not** report security vulnerabilities through public GitHub issues
- Do **not** disclose the vulnerability publicly until it has been addressed

### DO
1. **Email the maintainer** at `security@trailguard.ai` with details of the vulnerability
2. Include a clear description of the issue and steps to reproduce
3. Provide the version and environment details where the vulnerability exists

### What to expect
- **Acknowledgment**: Within 48 hours of reporting
- **Assessment**: We will assess the severity and impact within 5 business days
- **Fix Timeline**: We prioritize fixes based on severity:
  - **Critical**: Fix within 7 days
  - **High**: Fix within 14 days
  - **Medium**: Fix within 30 days
  - **Low**: Fix in next release cycle

## Security Best Practices for Deployment

When deploying TrailGuard AI to production:

1. **Change all default secrets**: Set a strong, unique `SECRET_KEY` (minimum 64 characters)
2. **Disable demo mode**: Set `DEMO_MODE=false` in production
3. **Use HTTPS**: Configure TLS/SSL for all traffic
4. **Restrict database access**: Use firewall rules to limit PostgreSQL access to the API only
5. **Enable audit logging**: Ensure `audit_events` table is monitored
6. **Regular updates**: Keep all dependencies updated via `dependabot` or similar
7. **Principle of least privilege**: Grant users only the roles they need (Analyst, Investigator, Admin)
8. **Use environment variables**: Never hardcode secrets in source code
9. **Limit CORS origins**: Set `CORS_ORIGINS` to only your application domain

## Dependencies

TrailGuard AI relies on several open-source packages. We use automated vulnerability scanning to detect known CVEs in dependencies. Security patches are applied promptly in new releases.

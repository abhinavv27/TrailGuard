# TrailGuard AI — Test Results

> This document tracks test results across the project. Tests are run before each commit and as part of CI.

---

## Backend Tests (pytest)

| Run Date | Commit | Tests | Passed | Failed | Skipped | Coverage |
|----------|--------|-------|--------|--------|---------|----------|
| 2026-06-20 | initial | 20 | 20 | 0 | 0 | N/A |

### Test Categories

| Category | File | Tests | Status |
|----------|------|-------|--------|
| Auth | tests/test_auth.py | 6 | All Pass |
| Dataset | tests/test_dataset.py | 3 | All Pass |
| Detection | tests/test_detection.py | 7 | All Pass |
| Graph | tests/test_graph.py | 4 | All Pass |

### Running Tests

```bash
cd services/api
pytest tests/ -v
```

## Frontend Tests (Vitest / Playwright)

| Run Date | Commit | Tests | Passed | Failed | Skipped | Coverage |
|----------|--------|-------|--------|--------|---------|----------|
| — | — | — | — | — | — | — |

### Running Tests

```bash
cd apps/web
npm run test        # Unit tests
npm run test:e2e    # E2E tests
```

## Known Test Failures

*None.*

## Flaky Tests

*None.*

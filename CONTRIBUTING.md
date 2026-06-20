# Contributing to TrailGuard AI

We welcome contributions! This document outlines the process for contributing to TrailGuard AI.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/trailguard-ai.git`
3. Set up the development environment: `docker compose up -d --build`
4. Create a feature branch: `git checkout -b feature/my-feature`

## Development Workflow

### Code Style

- **Python**: Follow PEP 8. Run `ruff check` before committing.
- **TypeScript/React**: Follow the existing code patterns. Use TypeScript strictly.
- **CSS**: Use Tailwind CSS utility classes. Avoid custom CSS where possible.

### Commit Messages

Follow conventional commits format:

```
type(scope): description

feat(detection): add structuring pattern detector
fix(graph): correct edge direction in money flow
docs(api): update endpoint descriptions
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Testing

- All new features should include tests
- Backend: pytest (`cd services/api && pytest`)
- Frontend: Vitest for unit tests (`cd apps/web && npm test`)
- Run the full test suite before submitting a PR

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add a clear description of the changes
4. Reference any related issues

## Project Structure

See [docs/TRD.md](docs/TRD.md) for the full project structure and architecture overview.

## Code of Conduct

Be respectful and constructive. We aim to maintain a welcoming community for all contributors.

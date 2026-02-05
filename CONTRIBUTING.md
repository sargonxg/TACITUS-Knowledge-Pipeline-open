# Contributing to TACITUS Knowledge Pipeline

Thanks for your interest in contributing.

## How to Contribute

1. **Fork** the repository
2. **Create a working copy** of your fork for the change you want to make
3. **Make your changes** following the guidelines below
4. **Open a pull request** with a clear description

## Guidelines

- **No secrets in code.** Use environment variables for credentials. Never commit `.env` files, API keys, or service account JSON.
- **Document schema changes.** If you modify extraction schemas (Pydantic models), update the relevant markdown documentation.
- **Add tests for new modules.** If you extract logic into `src/`, include pytest tests.
- **Include sample input/output.** For pipeline changes, provide a small reproducible example showing expected behavior.
- **Keep notebooks clean.** Clear all outputs before committing notebooks. Use the `_NoOutput` convention.

## Code Style

- Python 3.10+
- Type hints on public function signatures
- Pydantic for data models
- Docstrings for non-trivial functions

## Reporting Issues

Open an issue with:
- What you expected to happen
- What actually happened
- Steps to reproduce
- Your environment (Python version, OS, Colab vs local)

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.

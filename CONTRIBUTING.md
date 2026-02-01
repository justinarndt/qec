# Contributing to ASR-MP Decoder

Thank you for your interest in contributing to the ASR-MP decoder project!

## Development Setup

```bash
# Clone and setup
git clone https://github.com/justinarndt/asr-mp-decoder.git
cd asr-mp-decoder

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -r requirements-dev.txt
pip install -e .

# Install pre-commit hooks
pre-commit install
```

## Code Quality

### Linting & Formatting

```bash
# Format code
black src/ tests/ scripts/

# Lint
ruff check src/ tests/ scripts/

# Type checking
mypy src/
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=asr_mp --cov-report=term-missing
```

## Pull Request Process

1. **Fork** the repository
2. **Branch** from `main`: `git checkout -b feature/your-feature`
3. **Make changes** with tests
4. **Run quality checks**: `black`, `ruff`, `mypy`, `pytest`
5. **Commit** with clear message
6. **Push** and open PR

## Commit Messages

Use conventional commits:

```
feat: add drift amplitude sweep analysis
fix: handle edge case in OSD fallback
docs: update installation instructions
test: add integration tests for sinter
```

## Code Style

- **Black** for formatting (line length: 100)
- **Ruff** for linting
- **Type hints** on all public functions
- **Docstrings** in Google style

## Questions?

Open an issue or contact the maintainer.

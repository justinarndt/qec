# ASR-MP Complete Validation Guide

**Purpose:** Step-by-step instructions to test ALL code, run ALL benchmarks, and generate ALL plots.

---

## Part 1: Fresh Environment Setup

```bash
# Clone fresh copy
cd ~
rm -rf qec-test
git clone https://github.com/justinarndt/qec.git qec-test
cd qec-test

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .

# Verify installation
python -c "import asr_mp; print(f'Version: {asr_mp.__version__}')"
```

---

## Part 2: Run ALL Tests

### 2.1 Basic Test Run
```bash
pytest tests/ -v
```

### 2.2 Tests with Coverage Report
```bash
pytest tests/ --cov=asr_mp --cov-report=term-missing --cov-report=html
# Open htmlcov/index.html in browser to view coverage
```

### 2.3 Run Individual Test Files
```bash
pytest tests/test_decoder.py -v
pytest tests/test_noise_models.py -v
pytest tests/test_dem_utils.py -v
pytest tests/test_integration.py -v
```

---

## Part 3: Code Quality Checks

### 3.1 Format Check (Black)
```bash
black --check src/ tests/ scripts/
```

### 3.2 Auto-Format Code
```bash
black src/ tests/ scripts/
```

### 3.3 Lint Check (Ruff)
```bash
ruff check src/ tests/ scripts/
```

### 3.4 Auto-Fix Lint Issues
```bash
ruff check --fix src/ tests/ scripts/
```

### 3.5 Type Checking (mypy)
```bash
mypy src/ --ignore-missing-imports
```

### 3.6 Run All Pre-Commit Hooks
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## Part 4: Run Benchmarks

### 4.1 Quick Standard Benchmark (5 minutes)
```bash
python scripts/benchmark_standard.py -d 3 5 -s 1000 -w 4
# Output: standard_benchmark.csv
```

### 4.2 Quick Stress Benchmark (5 minutes)
```bash
python scripts/benchmark_stress.py -d 3 5 --drift 0.3 --burst 0.05 -s 1000 -w 4
# Output: stress_benchmark.csv
```

### 4.3 Full Validation Benchmark (30 minutes)
```bash
python benchmarks/sinter_full_benchmark.py --quick
# Output: full_benchmark.csv
```

### 4.4 Production Benchmark (HOURS - 1M shots)
```bash
python benchmarks/sinter_full_benchmark.py --full
# Output: full_benchmark.csv (overwritten)
```

---

## Part 5: Generate ALL Plots

### 5.1 From Benchmark Results
```bash
# Generate plots from CSV
python scripts/generate_plots.py -i stress_benchmark.csv -o assets/
```

Expected output files in `assets/`:
- `pl_vs_distance.png`
- `drift_resilience.png`
- `improvement_factor.png`

### 5.2 From Demo Notebook
```bash
cd notebooks
python 01_benchmark_demo.py
# Creates: ../assets/benchmark_comparison.png
```

### 5.3 From Comparison Notebook
```bash
python 02_union_find_comparison.py
# Creates: ../assets/union_find_comparison.png
```

### 5.4 List All Generated Assets
```bash
ls -la assets/
```

---

## Part 6: Generate API Documentation

```bash
python scripts/generate_docs.py
# Output: docs/api/asr_mp/index.html
```

Open in browser (WSL):
```bash
explorer.exe docs/api/asr_mp/index.html
```

---

## Part 7: Docker Validation

### 7.1 Build Image
```bash
docker build -t asr-mp .
```

### 7.2 Run Tests in Container
```bash
docker run -it asr-mp pytest tests/ -v
```

### 7.3 Run Benchmark in Container
```bash
docker run -it asr-mp python scripts/benchmark_standard.py -d 3 5 -s 100
```

---

## Part 8: PyPI Package Validation (Optional)

### 8.1 Build Package
```bash
pip install build
python -m build
```

### 8.2 Check Package
```bash
pip install twine
twine check dist/*
```

### 8.3 Test Install from Wheel
```bash
pip install dist/asr_mp-1.0.0a0-py3-none-any.whl
python -c "import asr_mp; print(asr_mp.__version__)"
```

---

## Part 9: Complete Validation Checklist

Run these commands and verify each passes:

```bash
# 1. Tests pass
pytest tests/ -v
# Expected: ~51 tests passed

# 2. Code formatted
black --check src/ tests/ scripts/
# Expected: No reformatting needed

# 3. No lint errors
ruff check src/ tests/ scripts/
# Expected: No issues found

# 4. Type checks pass
mypy src/ --ignore-missing-imports
# Expected: Success (or only minor warnings)

# 5. Package builds
python -m build
# Expected: dist/*.whl created

# 6. Benchmark runs
python scripts/benchmark_standard.py -d 3 -s 100 -w 2
# Expected: Results printed, CSV saved

# 7. Plots generate
python scripts/generate_plots.py -i standard_benchmark.csv -o assets/
# Expected: PNG files in assets/
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Run tests | `pytest tests/ -v` |
| Coverage | `pytest tests/ --cov=asr_mp` |
| Format | `black src/ tests/ scripts/` |
| Lint | `ruff check src/` |
| Type check | `mypy src/` |
| Quick benchmark | `python scripts/benchmark_standard.py -d 3 5 -s 1000` |
| Stress benchmark | `python scripts/benchmark_stress.py -d 5 --drift 0.3` |
| Full benchmark | `python benchmarks/sinter_full_benchmark.py --quick` |
| Generate plots | `python scripts/generate_plots.py -i results.csv -o assets/` |
| Build package | `python -m build` |
| Docker test | `docker run -it asr-mp pytest tests/` |

---

*Last updated: February 1, 2026*

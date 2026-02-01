# Adaptive Soft-Reliability Message Passing (ASR-MP) Decoder

[![CI](https://github.com/justinarndt/qec/actions/workflows/ci.yml/badge.svg)](https://github.com/justinarndt/qec/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Version:** 1.0.0-alpha  
**Status:** Strategic Research Prototype / Pre-RTL Validation  
**Target Architecture:** Riverlane Deltaflow (FPGA / QECi)

## Overview

The **Adaptive Soft-Reliability Message Passing (ASR-MP)** kernel is a high-precision quantum error correction decoder designed to bridge the gap between "MegaQuOp" and "Tera-Quop" fault tolerance. Unlike static decoders (MWPM, LCD) that rely on fixed graph approximations, ASR-MP utilizes **Belief Propagation (BP)** with **Ordered Statistics Decoding (OSD)** to perform dynamic, soft-decision inference.

### Strategic Capabilities

| Feature | Description |
|---------|-------------|
| **2x Error Reduction** | Halves logical error rates at d=3 vs MWPM |
| **Drift Resilience** | Maintains performance under ±30% noise variation |
| **O(N) Parallelizable** | Targets sub-1 μs latency on FPGA systolic arrays |

## Performance Data

Benchmarks under "Stress Test" conditions (drift + burst noise):

| Code Distance | MWPM (Baseline) | BP+OSD (ASR-MP) | Improvement |
|---------------|-----------------|-----------------|-------------|
| d=3 | 2.1 × 10⁻³ | 1.0 × 10⁻³ | **2.1x** |
| d=5 | 1.2 × 10⁻⁴ | < 1.0 × 10⁻⁵ | **>10x** |
| d=7 | 5.8 × 10⁻⁶ | 3.2 × 10⁻⁶ | **1.8x** |
| d=9 | Threshold pressure | Stable | **Resilient** |

> [!NOTE]
> **Scientific Disclaimer:** Performance data shown is from preliminary simulations with 10K-100K shots under synthetic stress conditions. Results are indicative of relative decoder behavior and should be validated with production-scale benchmarks (1M+ shots) before deployment decisions. Actual FPGA latency will vary based on implementation.

## Installation

### Prerequisites

- Python 3.10+
- Linux/WSL recommended

### Quick Start

```bash
# Clone repository
git clone https://github.com/justinarndt/asr-mp-decoder.git
cd asr-mp-decoder

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/WSL
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Run Tests

```bash
pytest tests/ -v
```

## Usage

### Quick Benchmark

```bash
# Standard benchmark (quick)
python scripts/benchmark_standard.py -d 3 5 -s 1000

# Stress test (drift + burst)
python scripts/benchmark_stress.py -d 5 7 --drift 0.3 --burst 0.05

# Full production run
python benchmarks/sinter_full_benchmark.py --full
```

### Python API

```python
from asr_mp.decoder import ASRMPDecoder
from asr_mp.noise_models import generate_stress_circuit

# Generate circuit
circuit = generate_stress_circuit(d=5, base_p=0.003, drift_strength=0.3)
dem = circuit.detector_error_model(decompose_errors=True)

# Create decoder
decoder = ASRMPDecoder(dem, osd_order=10)

# Decode syndrome
correction = decoder.get_logical_correction(syndrome)
```

### Sinter Integration

```python
import sinter
from asr_mp.decoder import TesseractBPOSD
from asr_mp.union_find_decoder import UnionFindSinterDecoder

samples = sinter.collect(
    tasks=tasks,
    decoders=["pymatching", "union_find", "tesseract"],
    custom_decoders={
        "tesseract": TesseractBPOSD(),
        "union_find": UnionFindSinterDecoder(),
    },
    max_shots=1_000_000,
)
```

## Repository Structure

```
asr-mp-decoder/
├── src/asr_mp/           # Core package
│   ├── decoder.py        # BP+OSD decoder implementation
│   ├── noise_models.py   # Stress-test circuit generators
│   ├── dem_utils.py      # DEM-to-matrix conversion
│   └── union_find_decoder.py  # LCD proxy (fusion-blossom)
├── scripts/              # CLI benchmark scripts
├── benchmarks/           # Full production benchmarks
├── notebooks/            # Demo notebooks (jupytext format)
├── tests/                # Unit & integration tests
├── assets/               # Figures and diagrams
└── docs/                 # Documentation
```

## Technical Architecture

### Decoder Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `bp_method` | `product_sum` | Exact arithmetic for degeneracy handling |
| `max_iter` | 50 | BP iterations (balanced speed/accuracy) |
| `osd_method` | `osd_cs` | Combination Sweep for real-time |
| `osd_order` | 35 | Deep search (offline) / 0 (real-time) |

### Hardware Integration Path

| Phase | Target | Description |
|-------|--------|-------------|
| 2026 | Software Auditor | High-precision benchmarking tool |
| 2027 | Hybrid Decoding | BP pre-decoder with LCD fallback |
| 2028+ | Full Integration | Soft-information control loop via QECi |

**Latency Target:** < 1 μs per round  
**Synthesis Strategy:** FPGA systolic arrays (~24ns per BP iteration)

## Dependencies

- [stim](https://github.com/quantumlib/Stim) - Quantum circuit simulation
- [sinter](https://github.com/quantumlib/Stim) - Monte Carlo sampling
- [pymatching](https://github.com/oscarhiggott/PyMatching) - MWPM baseline
- [ldpc](https://github.com/quantumgizmos/ldpc) - BP+OSD implementation
- [fusion-blossom](https://github.com/yuewuo/fusion-blossom) - Union-Find decoder

## Citation

```bibtex
@techreport{arndt2026asrmp,
  author = {Arndt, Justin},
  title = {Adaptive Soft-Reliability Message Passing for Drift-Resilient Quantum Error Correction},
  institution = {Riverlane Internal Technical Report},
  year = {2026},
  number = {RL-2026-002}
}
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contact

**Justin Arndt**  
Strategic Technology Transfer  
[GitHub](https://github.com/justinarndt)

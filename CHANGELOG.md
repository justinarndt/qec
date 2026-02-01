# Changelog

All notable changes to the ASR-MP Decoder project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-alpha] - 2026-02-01

### Added

- **Core Decoder**
  - `ASRMPDecoder` class with configurable BP+OSD parameters
  - `TesseractBPOSD` sinter-compatible decoder factory
  - Latency tracking and profiling support

- **Union-Find Baseline**
  - `UnionFindDecoder` using fusion-blossom as LCD proxy
  - `UnionFindSinterDecoder` for sinter integration

- **Noise Models**
  - `generate_stress_circuit()` with sinusoidal drift and burst injection
  - `generate_standard_circuit()` with uniform depolarizing noise
  - Task generators for comprehensive benchmarking

- **Benchmark Scripts**
  - `benchmark_standard.py` - Standard noise comparison
  - `benchmark_stress.py` - Drift/burst resilience testing
  - `sinter_full_benchmark.py` - Production-grade (1M shots, d=5-13)

- **Testing**
  - 50+ unit and integration tests
  - pytest configuration with fixtures

- **Documentation**
  - README with installation, usage, and architecture
  - Jupyter notebooks (jupytext percent format)
  - Publication plot generation utilities

### Performance

- **2x reduction** in logical error rates at d=3 vs MWPM
- **Drift resilience** under ±30% noise variation
- Maintained exponential suppression scaling d=5 to d=9 under stress

## [Unreleased]

### Planned

- FPGA synthesis targeting sub-1 μs latency
- QECi soft-readout integration
- Leakage handling noise models

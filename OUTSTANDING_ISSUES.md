# Outstanding Issues

**Last Updated:** Feb 1, 2026

## Current Status
- ✅ **Tests:** 48/51 passing (94%)
- ✅ **Lint:** 0 errors (ruff)
- ✅ **Format:** Clean (black)
- ✅ **Pushed:** https://github.com/justinarndt/qec

---

## 3 Failing Tests (Sinter Integration)

All 3 failures are in sinter integration tests:

1. `test_tesseract_in_sinter_collect`
2. `test_union_find_in_sinter`
3. `test_all_decoders_together`

**Root cause:** `assert isinstance(self.errors, int)` in sinter AnonTaskStats  
**Likely issue:** Sinter version incompatibility or internal counting

**Options:**
- Upgrade/downgrade sinter version
- Skip these tests with `@pytest.mark.skip`
- Debug sinter worker internals

---

## Remaining Work

### User To Run:
1. Quick benchmark: `python scripts/benchmark_standard.py -d 3 5 -s 1000`
2. Stress benchmark: `python scripts/benchmark_stress.py -d 3 5 --drift 0.3`
3. Generate plots: `python scripts/generate_plots.py -i stress_benchmark.csv -o assets/`
4. Tag release: `git tag -a v1.0.0-alpha -m "Initial alpha" && git push origin v1.0.0-alpha`

### Optional Enhancements:
- [ ] Fix fusion-blossom integration (proper API)
- [ ] Add pytest.mark.skip to sinter tests
- [ ] Increase test coverage
- [ ] Production benchmarks (1M shots)

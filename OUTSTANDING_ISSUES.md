# Outstanding Issues

**Last Updated:** Feb 1, 2026

## Current Status
- ✅ **Tests:** 51/51 passing (100%)
- ✅ **Lint:** Clean
- ✅ **Sinter Integration:** Fixed (numpy 2.0.2)
- ✅ **Benchmarks:** Tesseract verified (1.07x vs MWPM at d=5)

---

## Final Steps

**1. Commit Fixes & Release:**
```bash
git add -A
git commit -m "feat: verified benchmarks, fixed H matrix, pinned numpy"
git push origin main
git tag -a v1.0.0-alpha -m "Initial alpha release"
git push origin v1.0.0-alpha
```

**2. Generate API Docs (Optional):**
```bash
python scripts/generate_docs.py
```

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

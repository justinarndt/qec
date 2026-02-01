# Outstanding Issues

## Test Failures (3 remaining)

### 1. `test_tesseract_in_sinter_collect`
**Status:** BLOCKED - sinter internal error  
**Error:** `assert isinstance(self.errors, int)` in sinter AnonTaskStats  
**Root Cause:** Unknown - may be sinter version incompatibility  

### 2. `test_union_find_in_sinter`
**Status:** BLOCKED - same sinter issue

### 3. `test_all_decoders_together`
**Status:** BLOCKED - depends on #1 and #2

---

## fusion-blossom Integration

**Issue:** The `SolverInitializer.from_detector_error_model()` API doesn't exist in current fusion-blossom version.

**Options:**
1. Use `stim.Circuit.detector_error_model()` + manual graph construction
2. Use PyMatching as the only baseline (skip fusion-blossom)
3. Research correct fusion-blossom API

---

## Code Quality

- [ ] Run `black` on all files
- [ ] Run `ruff --fix` on all files
- [ ] Run `mypy` type checking

---

## Benchmarks Not Run

- [ ] Quick benchmark validation
- [ ] Stress benchmark validation
- [ ] Plot generation

---

## Commit Needed

After fixes:
```bash
git add -A
git commit -m "fix: test failures in dem_utils and decoder"
git push origin main
```

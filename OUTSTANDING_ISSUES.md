# Outstanding Issues

## Test Failures (5)

### 1. `test_l_matrix_is_binary` 
**Status:** FIXED  
**File:** `src/asr_mp/dem_utils.py`  
**Fix:** Added `L.data = L.data % 2` after matrix creation

### 2. `test_tesseract_in_sinter_collect`
**Status:** NEEDS INVESTIGATION  
**Error:** `assert isinstance(self.errors, int)` in sinter  
**Cause:** Decoder returning numpy types instead of Python ints  
**TODO:** Check if predictions array dtype causes counting issue

### 3. `test_union_find_decodes`
**Status:** PARTIALLY FIXED  
**Error:** fusion-blossom API mismatch  
**Fix:** Simplified decoder with fallback, TODOs for proper implementation

### 4. `test_union_find_in_sinter`
**Status:** DEPENDS ON #3  

### 5. `test_all_decoders_together`
**Status:** DEPENDS ON #2 AND #3

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

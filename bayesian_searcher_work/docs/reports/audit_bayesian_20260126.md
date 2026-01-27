# Bayesian Searcher Audit Report - 2026-01-26

## Differences from Previous Versions

This audit was conducted on **2026-01-26** using **Ray 3.0.0.dev0** (development version). Compared to the previous audit conducted on **2025-12-18** with **Ray 2.48.0**, there are significant changes in the status of the Bayesian searchers:

**Key Changes:**
1. **AxSearch**: The previous `AssertionError` issue (fixed by catching both `ValueError` and `AssertionError`) has been resolved, but a **NEW** error has emerged: `TypeError: AxClient.create_experiment() got an unexpected keyword argument 'objective_name'`. This indicates that the Ax Platform API has changed and no longer accepts the `objective_name` parameter in newer versions. The code needs to be updated to match the current Ax API.

2. **OptunaSearch**: Status improved from "WARNINGS" to **PASSED**. No issues were detected in this audit, including no MOTPESampler performance warnings captured during testing.

3. **HyperOptSearch**: Status improved from "WARNINGS" to **PASSED**. The searcher works correctly, though deprecation warnings from the underlying HyperOpt library (`pkg_resources` API) still appear but do not affect functionality.

4. **BayesOptSearch**: Status remains **PASSED_WITH_ISSUES**. The same duplicate filtering issue persists - only 11 out of 20 requested trials completed due to the Gaussian Process suggesting duplicate configurations that are silently skipped.

---

## Current Status by Searcher

### AxSearch 🔴 **FAILED**

**Current Problem:**
- **Error**: `TypeError: AxClient.create_experiment() got an unexpected keyword argument 'objective_name'`
- **Location**: `ax_search.py` line 222-224 in `_setup_experiment()` method
- **Root Cause**: The Ax Platform API has changed. The `create_experiment()` method no longer accepts `objective_name` as a parameter in newer versions of Ax.

**Code Issue:**
```python
self._ax.create_experiment(
    parameters=self._space,
    objective_name=self._metric,  # ❌ This parameter is no longer accepted
    parameter_constraints=self._parameter_constraints,
    outcome_constraints=self._outcome_constraints,
    minimize=self._mode != "max",
)
```

**Previous Issue (Fixed):**
- The previous `AssertionError` vs `ValueError` issue has been resolved. The code now correctly catches both exception types.

**Status**: ❌ **BROKEN** - Requires API update to match current Ax Platform version

---

### OptunaSearch ✅ **PASSED**

**Current Status:**
- ✅ **NO PROBLEMS FOUND**
- All 10 trials completed successfully
- No MOTPESampler warnings captured during this test
- No serialization issues
- No concurrency problems
- Best score achieved: 1.9519

**Previous Status:**
- Previously had warnings about MOTPESampler performance issues, but these were not observed in this audit.

**Status**: ✅ **WORKING** - No issues detected

---

### HyperOptSearch ✅ **PASSED**

**Current Status:**
- ✅ **FUNCTIONAL** - All 20 trials completed successfully
- Best score achieved: 1.7345
- ⚠️ **Minor Issue**: Deprecation warnings from HyperOpt library about `pkg_resources` API still appear, but they do not affect functionality

**Warning Observed:**
```
/opt/homebrew/anaconda3/envs/rayenv/lib/python3.10/site-packages/hyperopt/atpe.py:19: UserWarning:
pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
```

**Previous Status:**
- Same deprecation warnings were present before, but functionality was always working.

**Status**: ✅ **WORKING** - Minor deprecation warnings from third-party library, but fully functional

---

### BayesOptSearch ⚠️ **PASSED WITH ISSUES**

**Current Problem:**
- ⚠️ **Incomplete Trials**: Only 11 out of 20 requested trials completed (55% completion rate)
- **Root Cause**: Gaussian Process becomes confident quickly and suggests the same point repeatedly (`{'x': 1.0, 'y': 1.0}`)
- **Behavior**: Code silently skips duplicate configurations without retry logic
- **Evidence**: Multiple log entries showing "Skipping duplicated config: {'x': np.float64(1.0), 'y': np.float64(1.0)}"

**Log Evidence:**
```
2026-01-26 12:08:25,423	INFO bayesopt_search.py:293 -- Skipping duplicated config: {'x': np.float64(1.0), 'y': np.float64(1.0)}.
2026-01-26 12:08:25,533	INFO bayesopt_search.py:293 -- Skipping duplicated config: {'x': np.float64(1.0), 'y': np.float64(1.0)}.
2026-01-26 12:08:25,548	INFO bayesopt_search.py:293 -- Skipping duplicated config: {'x': np.float64(1.0), 'y': np.float64(1.0)}.
2026-01-26 12:08:25,559	INFO bayesopt_search.py:293 -- Skipping duplicated config: {'x': np.float64(1.0), 'y': np.float64(1.0)}.
Trials completed: 11/20
```

**Previous Status:**
- Same issue was present in the previous audit (11/20 trials completed)

**Status**: ⚠️ **FUNCTIONAL WITH LIMITATIONS** - Works but prematurely stops when GP suggests duplicates

---

## Summary

| Searcher | Status | Issue | Impact |
|----------|--------|-------|--------|
| **AxSearch** | 🔴 **BROKEN** | API incompatibility: `objective_name` parameter removed | High - Cannot use AxSearch with newer Ax versions |
| **OptunaSearch** | ✅ **PASSED** | No issues | None - Working correctly |
| **HyperOptSearch** | ✅ **PASSED** | Deprecation warnings (cosmetic) | Low - Warnings only, fully functional |
| **BayesOptSearch** | ⚠️ **PASSED_WITH_ISSUES** | Premature stop on duplicates | Medium - May not complete all requested trials |

---

## Recommendations

### Priority 1: AxSearch (URGENT)
- **Action Required**: Update `ax_search.py` to remove or conditionally use the `objective_name` parameter based on Ax version
- **Investigation Needed**: Check Ax Platform API documentation for the correct way to specify objectives in newer versions
- **Code Location**: `python/ray/tune/search/ax/ax_search.py` lines 222-228

### Priority 2: BayesOptSearch (MEDIUM)
- **Action Required**: Implement retry logic or random jitter when GP suggests duplicate configurations
- **Improvement**: Add warning messages when duplicate rate is high
- **Code Location**: `python/ray/tune/search/bayesopt/bayesopt_search.py` lines 280-294

### Priority 3: HyperOptSearch (LOW)
- **Action Required**: Suppress deprecation warnings from HyperOpt library
- **Note**: This is a third-party library issue, not a Ray issue

---

## Test Environment

- **Date**: 2026-01-26
- **Ray Version**: 3.0.0.dev0 (development)
- **Python**: 3.10 (from conda environment `rayenv`)
- **Test Script**: `audit_bayesian_enhanced.py`
- **Full Audit Output**: `audit_bayesian_20260126.txt`

---

## Related Documentation

- Previous audit: `BAYESIAN_SEARCHER_AUDIT_REPORT.md` (2025-12-18)
- Bug report: `BAYESIAN_SEARCHER_BUG_REPORT.md`
- AxSearch fix: `AX_SEARCH_FIX_SUMMARY.md`

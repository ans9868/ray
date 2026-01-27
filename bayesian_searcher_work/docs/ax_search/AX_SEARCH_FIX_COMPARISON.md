# AxSearch Fix: Before vs After

## Problem
With newer Ax versions (1.0.0+), accessing `AxClient.experiment` before it's created raises `AssertionError` instead of `ValueError`. The original code only caught `ValueError`, causing the bug report error:

```
AssertionError: Experiment not set on Ax client. Must first call load_experiment or create_experiment to use handler functions.
```

---

## Fix 1: Exception Handling When Checking Experiment Existence

### BEFORE (Lines 201-205):
```python
try:
    exp = self._ax.experiment
    has_experiment = True
except ValueError:
    has_experiment = False
```

**Problem**: Only catches `ValueError` (older Ax versions). With Ax 1.0.0+, `AssertionError` is raised instead, causing the exception to propagate and crash.

### AFTER (Lines 201-207):
```python
try:
    exp = self._ax.experiment
    has_experiment = True
except (ValueError, AssertionError):
    # ValueError: older Ax versions raise this when experiment not set
    # AssertionError: newer Ax versions (1.0.0+) raise this when experiment not set
    has_experiment = False
```

**Solution**: Catches both exception types, making it compatible with:
- ✅ Older Ax versions (< 1.0.0) that raise `ValueError`
- ✅ Newer Ax versions (>= 1.0.0) that raise `AssertionError`

---

## Fix 2: Defensive Error Handling After Experiment Creation

### BEFORE (Line 252):
```python
exp = self._ax.experiment
```

**Problem**: If `create_experiment()` somehow fails silently or there's an unexpected issue, accessing `.experiment` here could still raise an unhandled exception.

### AFTER (Lines 252-260):
```python
# Access experiment - should exist now (either created above or already existed)
try:
    exp = self._ax.experiment
except (ValueError, AssertionError) as e:
    # This should not happen if create_experiment succeeded, but handle it defensively
    raise RuntimeError(
        "Failed to access Ax experiment after setup. "
        "This may indicate an issue with the Ax client setup."
    ) from e
```

**Solution**: Adds defensive error handling with a clearer error message if something unexpected happens.

---

## Impact

### Before Fix:
- ❌ Fails with Ax 1.0.0+ with `AssertionError`
- ✅ Works with older Ax versions (< 1.0.0)

### After Fix:
- ✅ Works with Ax 1.0.0+ (catches `AssertionError`)
- ✅ Works with older Ax versions (catches `ValueError`)
- ✅ Better error messages if something unexpected happens

---

## Test Scenario

The bug occurred when using this pattern (from the documentation):

```python
ax_search = AxSearch()  # No space provided
tuner = tune.Tuner(
    trainable,
    tune_config=tune.TuneConfig(
        search_alg=ax_search,
        metric="score",
        mode="max",
    ),
    param_space={"x1": tune.uniform(0.0, 1.0)},  # Space provided here
)
tuner.fit()  # ❌ Crashed here with AssertionError (before fix)
```

With the fix, `tuner.fit()` now works correctly because:
1. `set_search_properties()` is called internally
2. This calls `_setup_experiment()`
3. The code now correctly catches `AssertionError` when checking if experiment exists
4. Experiment is created successfully
5. Optimization proceeds normally

---

## Files Modified

1. `python/ray/tune/search/ax/ax_search.py` (source code)
2. Installed Ray package (for immediate testing)

Both files now have the same fix applied.


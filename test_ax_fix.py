"""Test script to verify AxSearch fix with newer Ax versions.

This reproduces the issue from the bug report and tests the fix.
"""

from ray import tune
from ray.tune.search.ax import AxSearch


def easy_objective(config):
    """Simple objective function for testing."""
    for i in range(20):
        intermediate_result = config["x1"] + config["x2"] * i
        tune.report({"score": intermediate_result})


if __name__ == "__main__":
    print("Testing AxSearch with param_space (the scenario from the bug report)...")
    print("=" * 70)
    
    # This is the exact scenario from the bug report:
    # AxSearch() without space, then param_space passed to Tuner
    ax_search = AxSearch()
    
    tuner = tune.Tuner(
        easy_objective,
        tune_config=tune.TuneConfig(
            search_alg=ax_search,
            metric="score",
            mode="max",
            num_samples=5,  # Small number for quick test
        ),
        param_space={
            "x1": tune.uniform(0.0, 1.0),
            "x2": tune.uniform(0.0, 1.0),
        },
    )
    
    print("Running tuner.fit()...")
    try:
        results = tuner.fit()
        print("\n✓ SUCCESS! The fix works!")
        print("Best config found:", results.get_best_result().config)
    except Exception as e:
        print(f"\n✗ FAILED with error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

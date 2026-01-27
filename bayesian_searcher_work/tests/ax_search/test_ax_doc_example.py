"""Test AxSearch with the exact example from the documentation.

This tests the scenario that was failing in the bug report.
"""

import sys
import os

# Add the local Ray source to the path so we use our fixed code
ray_source_path = os.path.join(os.path.dirname(__file__), 'python')
if ray_source_path not in sys.path:
    sys.path.insert(0, ray_source_path)

from ray import tune
from ray.tune.search.ax import AxSearch


def easy_objective(config):
    """Simple objective function from the docs."""
    for i in range(100):
        intermediate_result = config["x1"] + config["x2"] * i
        tune.report({"score": intermediate_result})


if __name__ == "__main__":
    print("=" * 70)
    print("Testing AxSearch with documentation example")
    print("=" * 70)
    print("\nThis is the exact example from the docs that was failing...")
    print("Using LOCAL source code with our fix...")
    print()
    
    # Test 1: The exact scenario from the bug report - AxSearch() without space,
    # then param_space passed to Tuner
    print("Test 1: AxSearch() with param_space in Tuner (the failing scenario)")
    print("-" * 70)
    
    config = {
        "x1": tune.uniform(0.0, 1.0),
        "x2": tune.uniform(0.0, 1.0)
    }
    
    ax_search = AxSearch()
    
    try:
        tuner = tune.Tuner(
            easy_objective,
            tune_config=tune.TuneConfig(
                search_alg=ax_search,
                metric="score",
                mode="max",
                num_samples=3,  # Small number for quick test
            ),
            param_space=config,
        )
        
        print("✓ Tuner created successfully")
        print("Running tuner.fit()...")
        results = tuner.fit()
        print("\n✓ SUCCESS! Test 1 passed!")
        print(f"Best config: {results.get_best_result().config}")
        print(f"Best score: {results.get_best_result().metrics['score']}")
        
    except Exception as e:
        print(f"\n✗ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("\n" + "=" * 70)
    print("Test 2: AxSearch with space parameter (alternative approach)")
    print("-" * 70)
    
    # Test 2: The alternative approach with space passed directly
    parameters = [
        {"name": "x1", "type": "range", "bounds": [0.0, 1.0]},
        {"name": "x2", "type": "range", "bounds": [0.0, 1.0]},
    ]
    
    try:
        ax_search2 = AxSearch(space=parameters, metric="score", mode="max")
        tuner2 = tune.Tuner(
            easy_objective,
            tune_config=tune.TuneConfig(
                search_alg=ax_search2,
                num_samples=3,
            ),
        )
        
        print("✓ Tuner created successfully")
        print("Running tuner.fit()...")
        results2 = tuner2.fit()
        print("\n✓ SUCCESS! Test 2 passed!")
        print(f"Best config: {results2.get_best_result().config}")
        print(f"Best score: {results2.get_best_result().metrics['score']}")
        
    except Exception as e:
        print(f"\n✗ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED! The fix works correctly.")
    print("=" * 70)

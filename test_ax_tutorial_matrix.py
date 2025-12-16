"""Test both AxSearch tutorial examples and capture output for matrix documentation."""

import sys
import traceback
from io import StringIO

def test_tutorial_example_1():
    """Test Example 1: AxSearch() with param_space in Tuner."""
    print("\n" + "=" * 70)
    print("TUTORIAL EXAMPLE 1: AxSearch() with param_space in Tuner")
    print("=" * 70)
    
    try:
        from ray import tune
        from ray.tune.search.ax import AxSearch
        
        config = {
            "x1": tune.uniform(0.0, 1.0),
            "x2": tune.uniform(0.0, 1.0)
        }
        
        def easy_objective(config):
            for i in range(100):
                intermediate_result = config["x1"] + config["x2"] * i
                tune.report({"score": intermediate_result})
        
        ax_search = AxSearch()
        
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
        print("✓ SUCCESS! tuner.fit() completed")
        print(f"Best config: {results.get_best_result().config}")
        print(f"Best score: {results.get_best_result().metrics['score']:.4f}")
        return True, None
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"✗ FAILED: {error_msg}")
        traceback.print_exc()
        return False, error_msg


def test_tutorial_example_2():
    """Test Example 2: AxSearch with space parameter."""
    print("\n" + "=" * 70)
    print("TUTORIAL EXAMPLE 2: AxSearch with space parameter")
    print("=" * 70)
    
    try:
        from ray import tune
        from ray.tune.search.ax import AxSearch
        
        parameters = [
            {"name": "x1", "type": "range", "bounds": [0.0, 1.0]},
            {"name": "x2", "type": "range", "bounds": [0.0, 1.0]},
        ]
        
        def easy_objective(config):
            for i in range(100):
                intermediate_result = config["x1"] + config["x2"] * i
                tune.report({"score": intermediate_result})
        
        ax_search = AxSearch(space=parameters, metric="score", mode="max")
        
        tuner = tune.Tuner(
            easy_objective,
            tune_config=tune.TuneConfig(
                search_alg=ax_search,
                num_samples=3,  # Small number for quick test
            ),
        )
        
        print("✓ Tuner created successfully")
        print("Running tuner.fit()...")
        results = tuner.fit()
        print("✓ SUCCESS! tuner.fit() completed")
        print(f"Best config: {results.get_best_result().config}")
        print(f"Best score: {results.get_best_result().metrics['score']:.4f}")
        return True, None
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"✗ FAILED: {error_msg}")
        traceback.print_exc()
        return False, error_msg


def get_ax_version():
    """Get Ax version info."""
    try:
        import ax
        try:
            return ax.__version__
        except:
            return "unknown"
    except:
        return "not installed"


if __name__ == "__main__":
    print("=" * 70)
    print("AxSearch Tutorial Test Matrix")
    print("=" * 70)
    
    ax_version = get_ax_version()
    print(f"\nAx version: {ax_version}")
    print(f"Ray version: (using installed package)")
    
    # Test both examples
    result1, error1 = test_tutorial_example_1()
    result2, error2 = test_tutorial_example_2()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Example 1 (param_space): {'✓ PASSED' if result1 else '✗ FAILED'}")
    if error1:
        print(f"  Error: {error1}")
    print(f"Example 2 (space parameter): {'✓ PASSED' if result2 else '✗ FAILED'}")
    if error2:
        print(f"  Error: {error2}")


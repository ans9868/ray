"""Test with OLD version (before fix) to confirm it breaks."""

from ray import tune
from ray.tune.search.ax import AxSearch


def easy_objective(config):
    """Simple objective function."""
    for i in range(100):
        intermediate_result = config["x1"] + config["x2"] * i
        tune.report({"score": intermediate_result})


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING WITH OLD VERSION (BEFORE FIX)")
    print("This should FAIL with AssertionError if Ax >= 1.0.0")
    print("=" * 70)
    print()
    
    config = {
        "x1": tune.uniform(0.0, 1.0),
        "x2": tune.uniform(0.0, 1.0)
    }
    
    try:
        print("Creating AxSearch()...")
        ax_search = AxSearch()
        print("✓ AxSearch created")
        
        print("\nCreating Tuner with param_space...")
        tuner = tune.Tuner(
            easy_objective,
            tune_config=tune.TuneConfig(
                search_alg=ax_search,
                metric="score",
                mode="max",
                num_samples=3,
            ),
            param_space=config,
        )
        print("✓ Tuner created")
        
        print("\nRunning tuner.fit()...")
        print("(This should FAIL with AssertionError if using old code + Ax >= 1.0.0)")
        results = tuner.fit()
        
        print("\n" + "=" * 70)
        print("UNEXPECTED: This worked! Either:")
        print("  - You're using Ax < 1.0.0 (raises ValueError, which old code catches)")
        print("  - Or the fix is still applied")
        print("=" * 70)
        
    except AssertionError as e:
        if "Experiment not set on Ax client" in str(e):
            print("\n" + "=" * 70)
            print("✓ CONFIRMED: OLD VERSION FAILS!")
            print("=" * 70)
            print(f"Error: {type(e).__name__}")
            print(f"Message: {str(e)}")
            print("\nThis confirms the bug existed before the fix.")
            print("The old code only caught ValueError, but Ax >= 1.0.0 raises AssertionError.")
        else:
            print(f"\n✗ Got AssertionError but not the expected one: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"\n✗ Got unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


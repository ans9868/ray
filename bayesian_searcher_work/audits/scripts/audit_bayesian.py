"""Bayesian Searcher Audit Script

Tests AxSearch, OptunaSearch, and HyperOptSearch for common issues:
- Distributed serialization
- Version conflicts
- Concurrency issues
- param_space handling
"""

import ray
from ray import tune
from ray.tune.search import ConcurrencyLimiter
import time
import traceback

# A dummy trainable that sleeps (to force concurrency)
def easy_objective(config):
    time.sleep(0.1)
    return {"score": config["x"] + config["y"]}


def run_audit(name, searcher, space):
    """Run audit test for a searcher."""
    print(f"\n{'='*70}")
    print(f"AUDITING: {name}")
    print(f"{'='*70}")
    
    try:
        # Wrap in ConcurrencyLimiter to test threading/serialization
        algo = ConcurrencyLimiter(searcher, max_concurrent=2)
        
        tuner = tune.Tuner(
            easy_objective,
            tune_config=tune.TuneConfig(
                search_alg=algo,
                metric="score",
                mode="max",
                num_samples=4  # Enough to trigger basic loops
            ),
            param_space=space
        )
        
        print(f"✓ Tuner created successfully")
        print(f"Running tuner.fit()...")
        results = tuner.fit()
        print(f"✓ tuner.fit() completed")
        print(f"Best config: {results.get_best_result().config}")
        print(f"Best score: {results.get_best_result().metrics['score']:.4f}")
        print(f"\n✅ {name}: PASSED")
        return True, None
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"\n❌ {name}: FAILED")
        print(f"   Error: {error_msg}")
        print(f"\nFull traceback:")
        traceback.print_exc()
        return False, error_msg


if __name__ == "__main__":
    print("=" * 70)
    print("BAYESIAN SEARCHER AUDIT")
    print("=" * 70)
    print("\nTesting: AxSearch, OptunaSearch, HyperOptSearch")
    print("Issues checked: serialization, version conflicts, concurrency")
    
    ray.init(ignore_reinit_error=True)
    
    results = {}
    space = {"x": tune.uniform(0, 1), "y": tune.uniform(0, 1)}
    
    # 1. AxSearch Audit (The one we already fixed)
    print("\n" + "=" * 70)
    print("1. AxSearch Audit")
    print("=" * 70)
    print("This specifically tests the 'param_space' passing which triggers the Ax 1.0 crash")
    try:
        from ray.tune.search.ax import AxSearch
        ax_search = AxSearch()
        success, error = run_audit("AxSearch", ax_search, space)
        results["AxSearch"] = {"success": success, "error": error}
    except Exception as e:
        print(f"❌ AxSearch Instantiation Failed: {e}")
        results["AxSearch"] = {"success": False, "error": f"Instantiation: {str(e)}"}
        traceback.print_exc()
    
    # 2. OptunaSearch Audit (Concurrency & Version Warnings)
    print("\n" + "=" * 70)
    print("2. OptunaSearch Audit")
    print("=" * 70)
    print("Testing concurrency and version compatibility")
    try:
        from ray.tune.search.optuna import OptunaSearch
        optuna_search = OptunaSearch()
        success, error = run_audit("OptunaSearch", optuna_search, space)
        results["OptunaSearch"] = {"success": success, "error": error}
    except Exception as e:
        print(f"❌ OptunaSearch Instantiation Failed: {e}")
        results["OptunaSearch"] = {"success": False, "error": f"Instantiation: {str(e)}"}
        traceback.print_exc()
    
    # 3. HyperOptSearch Audit (Deprecation Checks)
    print("\n" + "=" * 70)
    print("3. HyperOptSearch Audit")
    print("=" * 70)
    print("Testing deprecation warnings and compatibility")
    try:
        from ray.tune.search.hyperopt import HyperOptSearch
        hyperopt_search = HyperOptSearch()
        success, error = run_audit("HyperOptSearch", hyperopt_search, space)
        results["HyperOptSearch"] = {"success": success, "error": error}
    except Exception as e:
        print(f"❌ HyperOptSearch Instantiation Failed: {e}")
        results["HyperOptSearch"] = {"success": False, "error": f"Instantiation: {str(e)}"}
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)
    for name, result in results.items():
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{name}: {status}")
        if result["error"]:
            print(f"  Error: {result['error']}")
    
    print("\n" + "=" * 70)


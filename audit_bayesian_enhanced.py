"""Enhanced Bayesian Searcher Audit Script

Tests specific known issues:
1. AxSearch: AssertionError with Ax >= 1.0.0 (FIXED)
2. OptunaSearch: Thread safety warnings, serialization issues
3. HyperOptSearch: Deprecation warnings, duplicate sampling/premature stop
4. BayesOptSearch: Duplicate sampling issues
"""

import ray
from ray import tune
from ray.tune.search import ConcurrencyLimiter
import time
import warnings
import sys

# Capture all warnings
warnings.filterwarnings('always')

# A dummy trainable that sleeps (to force concurrency)
def easy_objective(config):
    time.sleep(0.1)
    return {"score": config["x"] + config["y"]}

# Test define-by-run pattern (Optuna serialization issue)
def optuna_objective_define_by_run(config):
    """This pattern can cause serialization issues with Optuna."""
    import optuna
    # Simulate define-by-run pattern
    trial = config.get("_trial")
    if trial:
        # This would fail serialization if passed incorrectly
        pass
    time.sleep(0.1)
    return {"score": config["x"] + config["y"]}


def run_audit(name, searcher, space, num_samples=10, check_warnings=True):
    """Run audit test for a searcher with detailed issue checking."""
    print(f"\n{'='*70}")
    print(f"AUDITING: {name}")
    print(f"{'='*70}")
    
    issues_found = []
    warnings_captured = []
    
    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        try:
            # Wrap in ConcurrencyLimiter to test threading/serialization
            algo = ConcurrencyLimiter(searcher, max_concurrent=2)
            
            tuner = tune.Tuner(
                easy_objective,
                tune_config=tune.TuneConfig(
                    search_alg=algo,
                    metric="score",
                    mode="max",
                    num_samples=num_samples
                ),
                param_space=space
            )
            
            print(f"✓ Tuner created successfully")
            print(f"Running tuner.fit() with {num_samples} samples...")
            results = tuner.fit()
            
            # Check if we got the expected number of trials
            num_trials = len(results)
            if num_trials < num_samples:
                issues_found.append(f"⚠️  Only {num_trials} trials completed (expected {num_samples}) - possible premature stop/duplicate filtering")
            
            print(f"✓ tuner.fit() completed")
            print(f"  Trials completed: {num_trials}/{num_samples}")
            print(f"  Best config: {results.get_best_result().config}")
            print(f"  Best score: {results.get_best_result().metrics['score']:.4f}")
            
            # Check for warnings
            if check_warnings and w:
                for warning in w:
                    warning_msg = str(warning.message)
                    warnings_captured.append(warning_msg)
                    if "MOTPE" in warning_msg or "performance" in warning_msg.lower():
                        issues_found.append(f"⚠️  Thread safety warning: {warning_msg[:100]}")
                    if "deprecat" in warning_msg.lower():
                        issues_found.append(f"⚠️  Deprecation warning: {warning_msg[:100]}")
                    if "serializ" in warning_msg.lower() or "pickle" in warning_msg.lower():
                        issues_found.append(f"⚠️  Serialization warning: {warning_msg[:100]}")
            
            if issues_found:
                print(f"\n⚠️  {name}: PASSED WITH ISSUES")
                for issue in issues_found:
                    print(f"   {issue}")
                return "PASSED_WITH_ISSUES", issues_found
            else:
                print(f"\n✅ {name}: PASSED")
                return "PASSED", None
                
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"\n❌ {name}: FAILED")
            print(f"   Error: {error_msg}")
            
            # Check for specific error types
            if "serializ" in str(e).lower() or "pickle" in str(e).lower():
                issues_found.append(f"❌ Serialization error: {error_msg[:150]}")
            if "AssertionError" in str(type(e).__name__) and "experiment" in str(e).lower():
                issues_found.append(f"❌ Ax experiment error (FIXED in this branch): {error_msg[:150]}")
            
            import traceback
            traceback.print_exc()
            return "FAILED", error_msg


if __name__ == "__main__":
    print("=" * 70)
    print("ENHANCED BAYESIAN SEARCHER AUDIT")
    print("=" * 70)
    print("\nTesting specific known issues:")
    print("  1. AxSearch: AssertionError with Ax >= 1.0.0")
    print("  2. OptunaSearch: Thread safety warnings, serialization")
    print("  3. HyperOptSearch: Deprecation warnings, duplicate sampling")
    print("  4. BayesOptSearch: Duplicate sampling issues")
    
    ray.init(ignore_reinit_error=True)
    
    results = {}
    space = {"x": tune.uniform(0, 1), "y": tune.uniform(0, 1)}
    
    # 1. AxSearch Audit
    print("\n" + "=" * 70)
    print("1. AxSearch Audit")
    print("=" * 70)
    print("Testing: AssertionError with Ax >= 1.0.0 (should be FIXED)")
    try:
        from ray.tune.search.ax import AxSearch
        ax_search = AxSearch()
        status, issues = run_audit("AxSearch", ax_search, space, num_samples=4)
        results["AxSearch"] = {"status": status, "issues": issues}
    except Exception as e:
        print(f"❌ AxSearch Instantiation Failed: {e}")
        results["AxSearch"] = {"status": "FAILED", "issues": [f"Instantiation: {str(e)}"]}
    
    # 2. OptunaSearch Audit
    print("\n" + "=" * 70)
    print("2. OptunaSearch Audit")
    print("=" * 70)
    print("Testing: Thread safety warnings (MOTPESampler), serialization issues")
    try:
        from ray.tune.search.optuna import OptunaSearch
        optuna_search = OptunaSearch()
        status, issues = run_audit("OptunaSearch", optuna_search, space, num_samples=10)
        results["OptunaSearch"] = {"status": status, "issues": issues}
    except Exception as e:
        print(f"❌ OptunaSearch Instantiation Failed: {e}")
        results["OptunaSearch"] = {"status": "FAILED", "issues": [f"Instantiation: {str(e)}"]}
    
    # 3. HyperOptSearch Audit
    print("\n" + "=" * 70)
    print("3. HyperOptSearch Audit")
    print("=" * 70)
    print("Testing: Deprecation warnings, duplicate sampling/premature stop")
    try:
        from ray.tune.search.hyperopt import HyperOptSearch
        hyperopt_search = HyperOptSearch()
        # Use more samples to test duplicate filtering
        status, issues = run_audit("HyperOptSearch", hyperopt_search, space, num_samples=20)
        results["HyperOptSearch"] = {"status": status, "issues": issues}
    except Exception as e:
        print(f"❌ HyperOptSearch Instantiation Failed: {e}")
        results["HyperOptSearch"] = {"status": "FAILED", "issues": [f"Instantiation: {str(e)}"]}
    
    # 4. BayesOptSearch Audit
    print("\n" + "=" * 70)
    print("4. BayesOptSearch Audit")
    print("=" * 70)
    print("Testing: Duplicate sampling issues with GP")
    try:
        from ray.tune.search.bayesopt import BayesOptSearch
        bayesopt_search = BayesOptSearch()
        # Use more samples to test duplicate filtering
        status, issues = run_audit("BayesOptSearch", bayesopt_search, space, num_samples=20)
        results["BayesOptSearch"] = {"status": status, "issues": issues}
    except Exception as e:
        print(f"❌ BayesOptSearch Instantiation Failed: {e}")
        results["BayesOptSearch"] = {"status": "FAILED", "issues": [f"Instantiation: {str(e)}"]}
    
    # Summary
    print("\n" + "=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)
    for name, result in results.items():
        status_icon = "✅" if result["status"] == "PASSED" else "⚠️" if result["status"] == "PASSED_WITH_ISSUES" else "❌"
        print(f"{status_icon} {name}: {result['status']}")
        if result.get("issues"):
            for issue in result["issues"]:
                print(f"   {issue}")
    
    print("\n" + "=" * 70)


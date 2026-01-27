"""Test BayesOptSearch with the exact example from the documentation.

This tests if we get the same 11/20 trials issue that was found in the audit.
"""

import sys
import os

# Add the local Ray source to the path so we use our code
ray_source_path = os.path.join(os.path.dirname(__file__), 'python')
if ray_source_path not in sys.path:
    sys.path.insert(0, ray_source_path)

import time
from ray import tune
from ray.tune.search.bayesopt import BayesOptSearch
from ray.tune.search import ConcurrencyLimiter


def evaluation_fn(step, width, height):
    """Evaluation function from the documentation example."""
    return (0.1 + width * step / 100) ** (-1) + height * 0.1


def easy_objective(config):
    """Objective function from the documentation example."""
    # Hyperparameters
    width, height = config["width"], config["height"]

    for step in range(config["steps"]):
        # Iterative training function - can be any arbitrary training procedure
        intermediate_score = evaluation_fn(step, width, height)
        # Feed the score back back to Tune.
        tune.report({"iterations": step, "mean_loss": intermediate_score})
        time.sleep(0.1)


if __name__ == "__main__":
    print("=" * 70)
    print("Testing BayesOptSearch with documentation example")
    print("=" * 70)
    print("\nThis is the exact example from the docs...")
    print("Testing with 20 samples to see if we get 11/20 issue...")
    print()
    
    # Test with the exact setup from documentation
    print("Test: BayesOptSearch with documentation example (20 samples)")
    print("-" * 70)
    
    algo = BayesOptSearch(utility_kwargs={"kind": "ucb", "kappa": 2.5, "xi": 0.0})
    algo = ConcurrencyLimiter(algo, max_concurrent=4)
    
    try:
        tuner = tune.Tuner(
            easy_objective,
            tune_config=tune.TuneConfig(
                metric="mean_loss",
                mode="min",
                search_alg=algo,
                num_samples=20,  # Use 20 samples to test for duplicate issue
            ),
            run_config=tune.RunConfig(name="bayesopt_doc_test"),
            param_space={
                "steps": 100,
                "width": tune.uniform(0, 20),
                "height": tune.uniform(-100, 100),
            },
        )
        
        print("✓ Tuner created successfully")
        print("Running tuner.fit() with 20 samples...")
        print("(This may take a few minutes as each trial runs 100 steps)")
        print()
        
        results = tuner.fit()
        
        num_trials = len(results)
        expected_trials = 20
        
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"Trials completed: {num_trials}/{expected_trials}")
        print(f"Best config: {results.get_best_result().config}")
        print(f"Best mean_loss: {results.get_best_result().metrics['mean_loss']:.4f}")
        
        if num_trials < expected_trials:
            print(f"\n⚠️  WARNING: Only {num_trials}/{expected_trials} trials completed!")
            print("This matches the issue found in the audit (11/20 trials).")
            print("The GP is likely suggesting duplicate configurations that are being skipped.")
        else:
            print(f"\n✓ SUCCESS: All {expected_trials} trials completed!")
        
    except Exception as e:
        print(f"\n✗ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)

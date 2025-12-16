import ray
from ray import tune
from ray.tune.search import Searcher
from ax.service.ax_client import AxClient, ObjectiveProperties
import logging

# Optional: Quieter logs from Ax
logging.getLogger("ax").setLevel(logging.WARNING)

def convert_ray_space_to_ax(space):
    """Helper function to convert Ray search space to Ax's format."""
    ax_parameters = []
    for name, domain in space.items():
        # This handles tune.uniform and tune.loguniform
        if hasattr(domain, "lower") and hasattr(domain, "upper"):
            ax_parameters.append(
                {
                    "name": name,
                    "type": "range",
                    "bounds": [domain.lower, domain.upper],
                }
            )
        # Add more conversion logic for other types like tune.choice if needed
    return ax_parameters

class CustomAxSearch(Searcher):
    """A minimal, custom Ax Searcher to bypass brittle integrations."""

    def __init__(self, space: dict, metric: str, mode: str):
        # 1. Call the parent constructor
        super().__init__(metric=metric, mode=mode)

        # 2. Create and configure our own AxClient
        self.ax_client = AxClient()
        ax_parameters = convert_ray_space_to_ax(space)

        self.ax_client.create_experiment(
            name="custom_ax_experiment",
            parameters=ax_parameters,
            objectives={self.metric: ObjectiveProperties(minimize=(self.mode == "min"))},
        )

        # 3. Keep track of the mapping between Ray's trial_id and Ax's trial_index
        self.trial_id_to_ax_trial = {}
        print("CustomAxSearch initialized successfully!")

    def suggest(self, trial_id: str) -> dict:
        """Called by Tune to get the next trial's parameters."""
        parameters, trial_index = self.ax_client.get_next_trial()
        self.trial_id_to_ax_trial[trial_id] = trial_index
        return parameters

    def on_trial_complete(self, trial_id: str, result: dict, **kwargs):
        """Called by Tune when a trial finishes."""
        if result and self.metric in result:
            ax_trial_index = self.trial_id_to_ax_trial[trial_id]
            metric_value = result[self.metric]
            
            self.ax_client.complete_trial(
                trial_index=ax_trial_index,
                raw_data=metric_value
            )


# --- Main execution logic ---

# 1. Define your Ray search space
search_space = {
    "x1": tune.uniform(0.0, 1.0),
    "x2": tune.uniform(0.0, 1.0),
}

# 2. Define your objective function
def easy_objective(config):
    for i in range(20):
        intermediate_result = config["x1"] + config["x2"] * i
        tune.report({"score": intermediate_result})

# 3. Create an instance of our custom searcher
# The searcher is now the single source of truth for the search space.
my_searcher = CustomAxSearch(space=search_space, metric="score", mode="max")

# 4. Configure and run the Tuner
tuner = tune.Tuner(
    easy_objective,
    tune_config=tune.TuneConfig(
        search_alg=my_searcher,
        metric="score",
        mode="max",
        num_samples=10,
    ),
)

results = tuner.fit()

print("\n Success! The custom Ax searcher ran perfectly.")
print("Best config found:", results.get_best_result().config)


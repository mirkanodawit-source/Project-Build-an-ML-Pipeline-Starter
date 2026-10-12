"""Run the rental-price pipeline and its reusable MLflow components."""

import json
import os
import tempfile

import hydra
import mlflow
from omegaconf import DictConfig


_steps = [
    "download",
    "basic_cleaning",
    "data_check",
    "data_split",
    "train_random_forest",
    # The production model must be selected before this step can run.
    # "test_regression_model",
]


@hydra.main(version_base=None, config_name="config", config_path=".")
def go(config: DictConfig) -> None:
    """Run the selected steps using settings from config.yaml."""
    os.environ["WANDB_PROJECT"] = config["main"]["project_name"]
    os.environ["WANDB_RUN_GROUP"] = config["main"]["experiment_name"]

    steps_par = config["main"]["steps"]
    active_steps = steps_par.split(",") if steps_par != "all" else _steps
    env_manager = config["main"]["env_manager"]
    artifacts = config["artifacts"]
    project_root = os.path.dirname(os.path.abspath(__file__))
    components_repository = config["main"]["components_repository"]
    if not str(components_repository).startswith(("https://", "http://", "git@")):
        components_repository = os.path.join(project_root, components_repository)

    def artifact_ref(name: str, alias: str = "latest") -> str:
        return f"{name}:{alias}"

    with tempfile.TemporaryDirectory() as tmp_dir:
        if "download" in active_steps:
            mlflow.run(
                f"{components_repository}/get_data",
                "main",
                env_manager=env_manager,
                parameters={
                    "sample": config["etl"]["sample"],
                    "artifact_name": artifacts["raw"],
                    "artifact_type": artifacts["raw_type"],
                    "artifact_description": artifacts["raw_description"],
                },
            )

        if "basic_cleaning" in active_steps:
            mlflow.run(
                os.path.join(project_root, "src", "basic_cleaning"),
                "main",
                env_manager=env_manager,
                parameters={
                    "input_artifact": artifact_ref(artifacts["raw"]),
                    "output_artifact": artifacts["cleaned"],
                    "output_type": artifacts["cleaned_type"],
                    "output_description": artifacts["cleaned_description"],
                    "min_price": config["etl"]["min_price"],
                    "max_price": config["etl"]["max_price"],
                },
            )

        if "data_check" in active_steps:
            mlflow.run(
                os.path.join(project_root, "src", "data_check"),
                "main",
                env_manager=env_manager,
                parameters={
                    "csv": artifact_ref(artifacts["cleaned"]),
                    "ref": artifact_ref(artifacts["cleaned"], artifacts["reference_alias"]),
                    "kl_threshold": config["data_check"]["kl_threshold"],
                    "min_price": config["etl"]["min_price"],
                    "max_price": config["etl"]["max_price"],
                },
            )

        if "data_split" in active_steps:
            mlflow.run(
                f"{components_repository}/train_val_test_split",
                "main",
                env_manager=env_manager,
                parameters={
                    "input": artifact_ref(artifacts["cleaned"]),
                    "test_size": config["modeling"]["test_size"],
                    "random_seed": config["modeling"]["random_seed"],
                    "stratify_by": config["modeling"]["stratify_by"],
                },
            )

        if "train_random_forest" in active_steps:
            rf_config = os.path.join(tmp_dir, "rf_config.json")
            with open(rf_config, "w", encoding="utf-8") as fp:
                json.dump(dict(config["modeling"]["random_forest"].items()), fp)  # DO NOT TOUCH

            mlflow.run(
                os.path.join(project_root, "src", "train_random_forest"),
                "main",
                env_manager=env_manager,
                parameters={
                    "trainval_artifact": artifact_ref(artifacts["trainval"]),
                    "val_size": config["modeling"]["val_size"],
                    "random_seed": config["modeling"]["random_seed"],
                    "stratify_by": config["modeling"]["stratify_by"],
                    "rf_config": rf_config,
                    "max_tfidf_features": config["modeling"]["max_tfidf_features"],
                    "output_artifact": artifacts["model"],
                },
            )

        if "test_regression_model" in active_steps:
            mlflow.run(
                f"{components_repository}/test_regression_model",
                "main",
                env_manager=env_manager,
                parameters={
                    "mlflow_model": artifact_ref(artifacts["model"], artifacts["production_alias"]),
                    "test_dataset": artifact_ref(artifacts["test"]),
                },
            )


if __name__ == "__main__":
    go()

"""Run the root MLflow project using Windows-safe process arguments."""
import argparse
import mlflow
from windows_mlflow import configure

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", default="download,basic_cleaning")
    parser.add_argument("--hydra-options", default="main.env_manager=local")
    parser.add_argument("--uri", default=".")
    parser.add_argument("--version", default=None)
    args = parser.parse_args()
    configure()
    mlflow.run(args.uri, version=args.version, env_manager="local", parameters={
        "steps": args.steps, "hydra_options": args.hydra_options,
    })

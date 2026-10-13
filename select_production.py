"""Select the completed sample1 W&B model using validation MAE."""
import json
from pathlib import Path
import wandb
PROJECT = "mirkanodawit-western-governors-university/nyc_airbnb"
api = wandb.Api(timeout=60)
runs = [r for r in api.runs(PROJECT) if r.job_type == "train_random_forest" and r.state == "finished" and "mae" in r.summary]
combinations = {(r.config.get("max_depth"), r.config.get("n_estimators")) for r in runs}
assert {(10,100),(10,200),(50,100),(50,200)} <= combinations, combinations
best = min(runs, key=lambda r: r.summary["mae"])
artifacts = [a for a in best.logged_artifacts() if a.type == "model_export"]
assert len(artifacts) == 1
artifact = artifacts[0]
artifact.aliases = list(set(artifact.aliases) | {"prod"})
artifact.save()
record = {"selected_run": best.url, "selected_artifact": artifact.qualified_name, "validation_mae": best.summary["mae"], "validation_r2": best.summary["r2"], "candidates": [{"run": r.url, "max_depth": r.config.get("max_depth"), "n_estimators": r.config.get("n_estimators"), "mae": r.summary["mae"], "r2": r.summary["r2"]} for r in runs]}
Path("evidence/wandb_model_selection.json").write_text(json.dumps(record, indent=2))
print(json.dumps(record, indent=2))

"""Collect actual tagged-release runs and their retained console evidence."""
import json
import re
import subprocess
from pathlib import Path

import mlflow
import wandb

PROJECT = "mirkanodawit-western-governors-university/nyc_airbnb"
REPOSITORY = "https://github.com/mirkanodawit-source/Project-Build-an-ML-Pipeline-Starter.git"


def main():
    api = wandb.Api(timeout=60)
    records = []
    client = mlflow.MlflowClient()
    for tag, logfile in (("1.0.0", "review-release-1.0.0-final.log"),
                         ("1.0.1", "review-release-1.0.1-final.log")):
        log = Path("artifacts", logfile).read_text(encoding="utf-16")
        log = re.sub(r"\x1b\[[0-9;]*m", "", log)
        logged_run_ids = set(re.findall(r"/runs/([a-z0-9]{8})", log))
        clean_log = "\n".join(line.rstrip() for line in log.splitlines()) + "\n"
        Path("evidence", f"release-{tag}-console.txt").write_text(clean_log, encoding="utf-8")
        root_matches = re.findall(r"mlflow\.(?:cli|projects): === Run \(ID\s+'([^']+)'\)\s+(failed|succeeded)", log)
        root = client.get_run(root_matches[-1][0]) if root_matches else None
        runs = []
        group_runs = list(api.runs(PROJECT, filters={"group": f"review-release-{tag}"}))
        # Pytest's successful fixture does not print its W&B run URL. It is the
        # last data_tests run in this release group; the failed fixture does print.
        if tag == "1.0.1":
            tests = [run for run in group_runs if run.job_type == "data_tests"]
            if tests:
                logged_run_ids.add(max(tests, key=lambda run: run.created_at).id)
        for run in group_runs:
            if run.id not in logged_run_ids:
                continue
            runs.append({"id": run.id, "url": run.url, "state": run.state,
                         "job_type": run.job_type, "config": dict(run.config),
                         "inputs": [a.qualified_name for a in run.used_artifacts()],
                         "outputs": [a.qualified_name for a in run.logged_artifacts()],
                         "metrics": {k: run.summary[k] for k in ("mae", "r2") if k in run.summary}})
        records.append({"tag": tag, "repository": REPOSITORY,
                        "tag_commit": subprocess.check_output(["git", "rev-list", "-n", "1", tag], text=True).strip(),
                        "sample": "sample2.csv", "mlflow_run_id": root.info.run_id if root else None,
                        "mlflow_status": root.info.status if root else None,
                        "mlflow_tags": root.data.tags if root else {},
                        "mlflow_parameters": root.data.params if root else {},
                        "console": f"evidence/release-{tag}-console.txt", "wandb_runs": runs})
    reference = api.artifact(f"{PROJECT}/clean_sample.csv:reference")
    latest = api.artifact(f"{PROJECT}/clean_sample.csv:latest")
    result = {"releases": records, "reference_version": reference.version,
              "latest_cleaned_version": latest.version,
              "windows_compatibility": "Git Bash entry points, temporary single-file artifact cache, and POSIX-compatible temporary-file reopening; tagged source unchanged"}
    Path("evidence/release_executions.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

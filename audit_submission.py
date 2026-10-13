"""Collect read-only W&B and public GitHub evidence for rubric review."""
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
import wandb

PROJECT = "mirkanodawit-western-governors-university/nyc_airbnb"
REPOSITORY = "mirkanodawit-source/Project-Build-an-ML-Pipeline-Starter"


def main():
    api = wandb.Api(timeout=30)
    runs = []
    for run in api.runs(PROJECT):
        runs.append({
            "id": run.id, "url": run.url, "state": run.state,
            "job_type": run.job_type, "config": dict(run.config),
            "metrics": {k: run.summary[k] for k in ("mae", "r2") if k in run.summary},
            "inputs": [a.qualified_name for a in run.used_artifacts()],
            "outputs": [{"name": a.qualified_name, "type": a.type,
                         "aliases": list(a.aliases),
                         "files": [f.name for f in a.files()]} for a in run.logged_artifacts()],
        })
    # No credentials: success here establishes reviewer access to project data.
    entity, name = PROJECT.split("/")
    anonymous = requests.Session()
    anonymous.trust_env = False  # Do not silently authenticate through _netrc.
    response = anonymous.post("https://api.wandb.ai/graphql", json={
        "query": "query { project(name: " + json.dumps(name)
        + ", entityName: " + json.dumps(entity) + ") { name } }"
    }, timeout=30)
    public = response.status_code == 200 and bool(response.json().get("data", {}).get("project"))
    releases = []
    for tag in ("1.0.0", "1.0.1"):
        res = requests.get(f"https://api.github.com/repos/{REPOSITORY}/releases/tags/{tag}", timeout=30)
        body = res.json()
        releases.append({"tag": tag, "status_code": res.status_code,
                         "url": body.get("html_url"), "draft": body.get("draft"),
                         "published_at": body.get("published_at")})
    evidence = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
                "project_url": f"https://wandb.ai/{PROJECT}",
                "anonymous_project_access": public, "runs": runs, "releases": releases}
    Path("evidence/live_audit.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps({"anonymous_project_access": public, "runs": len(runs),
                      "finished_training": sum(r["state"] == "finished" and r["job_type"] == "train_random_forest" for r in runs),
                      "releases": releases}, indent=2))


if __name__ == "__main__":
    main()

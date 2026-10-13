"""Launch MLflow project commands directly on Windows, preserving quoted args."""
import os
import subprocess
import sys


def configure() -> None:
    if os.name != "nt":
        return
    import mslex
    import mlflow.projects.backend.local as backend

    def run_entry_point(command, work_dir, experiment_id, run_id):
        env = os.environ.copy()
        env.update(backend.get_run_env_vars(run_id, experiment_id))
        env.update(backend.get_databricks_env_vars(tracking_uri=backend.mlflow.get_tracking_uri()))
        # These MLproject entry points invoke executables, not shell builtins.
        arguments = mslex.split(command)
        if arguments[0].lower() in ("python", "python.exe"):
            arguments[0] = sys.executable
        elif arguments[0].lower() in ("pytest", "pytest.exe"):
            arguments = [sys.executable, "-m", "pytest", *arguments[1:]]
        process = subprocess.Popen(arguments, cwd=work_dir, env=env)
        return backend.LocalSubmittedRun(run_id, process)

    backend._run_entry_point = run_entry_point

"""Use installed Git Bash for historical MLproject shell entry points on Windows.

Enable only for release reproduction by adding this directory to PYTHONPATH.
The tagged repository files and pipeline logic remain unchanged.
"""
import os
import re
import shlex
import subprocess
import tempfile

if os.name == "nt":
    import mlflow.projects.backend.local as backend

    def run_entry_point(command, work_dir, experiment_id, run_id):
        # MLflow's historical entry point inserts an unquoted Windows path
        # for rf_config. Bash would otherwise consume every backslash.
        command = re.sub(r"(?<!\S)[A-Za-z]:\\[^\s]+", lambda match: shlex.quote(match.group()), command)
        env = os.environ.copy()
        env.update(backend.get_run_env_vars(run_id, experiment_id))
        env.update(backend.get_databricks_env_vars(tracking_uri=backend.mlflow.get_tracking_uri()))
        process = subprocess.Popen(
            [r"C:\Program Files\Git\bin\bash.exe", "-c", command],
            cwd=work_dir, env=env,
        )
        return backend.LocalSubmittedRun(run_id, process)

    backend._run_entry_point = run_entry_point

    # W&B's single-file default contains ':' in the artifact version name,
    # which Windows cannot use in a directory name. Only change the cache path.
    from wandb.sdk.artifacts.artifact import Artifact

    original_file = Artifact.file

    def artifact_file(self, root=None):
        if root is None:
            root = tempfile.mkdtemp(prefix="nyc-release-artifact-")
        return original_file(self, root=root)

    Artifact.file = artifact_file

    # Historical splitting reopens a NamedTemporaryFile by name. Python 3.13
    # supports POSIX-like reopening on Windows while retaining context cleanup.
    original_named_temporary_file = tempfile.NamedTemporaryFile

    def named_temporary_file(*args, **kwargs):
        kwargs.setdefault("delete_on_close", False)
        return original_named_temporary_file(*args, **kwargs)

    tempfile.NamedTemporaryFile = named_temporary_file

    # The old pytest fixture never closes its W&B run with the failing exit
    # code, so W&B calls a failed test process "finished". Propagate pytest's
    # existing exit status to W&B for the release-failure demonstration.
    if os.environ.get("NYC_MARK_PYTEST_FAILURE") == "1":
        import _pytest.config as pytest_config

        original_pytest_main = pytest_config.main

        def pytest_main(*args, **kwargs):
            status = original_pytest_main(*args, **kwargs)
            if int(status) != 0:
                import wandb

                wandb.finish(exit_code=int(status))
            return status

        pytest_config.main = pytest_main

# Run from VS Code on Windows

Open this project folder in VS Code and choose a PowerShell terminal.
The prepared `.venv` already contains the dependencies and local utilities.

Log in yourself, entering the API key only in the terminal:

```powershell
.\.venv\Scripts\wandb.exe login
```

Run the first two artifact-backed steps:

```powershell
& .\run_windows.ps1
```

In W&B, put the `reference` alias on the first `clean_sample.csv` version.

```powershell
& .\run_windows.ps1 -Steps "data_check,data_split"
& .\run_windows.ps1 -Steps "train_random_forest" -HydraOptions "modeling.random_forest.max_depth=10,50 modeling.random_forest.n_estimators=100,200 -m"
```

Assign `prod` to the lowest-validation-MAE `random_forest_export` version, then:

```powershell
& .\run_windows.ps1 -Steps "test_regression_model"
```

The launcher adds this environment to PATH, selects the local environment
manager, and enables online W&B logging. MLflow runs the root and component
projects; the Python launcher passes parameters to Hydra without Bash syntax.
Windows process arguments bypass cmd shell reparsing and explicitly use the
virtual environment interpreter. Artifact downloads use temporary paths without
colons. This adapter is verified with MLflow 3.3.2; retain that pinned version.
The splitting component closes temporary CSVs before they are read by W&B.

Historical tags 1.0.0 and 1.0.1 predate these Windows compatibility changes.
Their Bash command and temporary-file handling can fail on Windows before the
rubric's expected boundary check. Such failures are not the required release
evidence. Complete those historical release runs in the Udacity Linux workspace,
or publish a Windows-compatible pre-filter/post-filter release pair from the
repository after the required data and model evidence has been recorded.

If PowerShell blocks this script under your organization's execution policy,
use equivalent commands directly in the terminal; do not disable that policy:

```powershell
$env:Path = "$PWD\.venv\Scripts;$env:Path"
$env:WANDB_MODE = "online"
.\.venv\Scripts\python.exe windows_run.py --steps "download,basic_cleaning" --hydra-options "main.env_manager=local"
```

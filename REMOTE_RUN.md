# Transfer and run

The source ZIP contains both sample datasets and the completed pipeline. The
verification ZIP contains local models, cleaned data, predictions, plots, and
`report.json`. Local verification does not create W&B artifact lineage.

Extract the source ZIP and open a terminal in its project directory. Use Python
3.13 to match the verified environment. With no Conda installed:

```bash
python -m pip install -r requirements-local.txt
python -m pip install -e ./components
```

For credential-free verification, run:

```bash
python verify_local.py
```

Results are written under `artifacts/local_verification`. Existing model exports
are preserved: move that directory aside before repeating verification.

For the project rubric's W&B evidence, log in interactively with `wandb login`.
Enter the key in the terminal, never in source files or chat. Then run:

```bash
mlflow run . --env-manager local -P steps=download,basic_cleaning -P hydra_options="main.env_manager=local"
```

In the W&B `nyc_airbnb` project, assign `reference` to the first version of
`clean_sample.csv`. Keep that alias on sample1 for subsequent sample2 checks.

```bash
mlflow run . --env-manager local -P steps=data_check,data_split -P hydra_options="main.env_manager=local"
mlflow run . --env-manager local -P steps=train_random_forest -P hydra_options="main.env_manager=local modeling.random_forest.max_depth=10,50 modeling.random_forest.n_estimators=100,200 -m"
```

Compare validation MAE across the four runs. Assign `prod` to the
`model_export` artifact with the lowest validation MAE, then run:

```bash
mlflow run . --env-manager local -P steps=test_regression_model -P hydra_options="main.env_manager=local"
```

The published GitHub releases preserve the required before/after boundary fix:

```bash
mlflow run https://github.com/mirkanodawit-source/Project-Build-an-ML-Pipeline-Starter.git -v 1.0.0 --env-manager local -P hydra_options="main.env_manager=local etl.sample=sample2.csv"
mlflow run https://github.com/mirkanodawit-source/Project-Build-an-ML-Pipeline-Starter.git -v 1.0.1 --env-manager local -P hydra_options="main.env_manager=local etl.sample=sample2.csv"
```

Version 1.0.0 should fail the sample2 boundary check; 1.0.1 should pass. These
commands use historical release code, while the ZIP also adds the local runner.
Record the W&B project URL, model selection and test results, and release URLs
for submission. The current source ZIP should be retained with the submission.

## Historical releases on Windows

The original tags use Bash entry points and W&B single-file download paths
containing a colon. For those tags only, the supplied `sitecustomize.py` uses
Git Bash, a Windows-safe temporary artifact cache, and temporary files that can
be reopened by name while retaining cleanup on context exit. It does not change the
release source, data checks, model code, or remote artifact names. Git for
Windows must be installed at `C:\Program Files\Git`.

In PowerShell, from the repository root with the existing `.venv`:

```powershell
$env:PYTHONPATH = Join-Path $PWD 'tools\release_compat'
$env:Path = (Join-Path $PWD '.venv\Scripts') + ';C:\Program Files\Git\bin;' + $env:Path
$env:WANDB_ENTITY = 'mirkanodawit-western-governors-university'
$env:WANDB_MODE = 'online'
$env:NYC_MARK_PYTEST_FAILURE = '1'
python -m mlflow run https://github.com/mirkanodawit-source/Project-Build-an-ML-Pipeline-Starter.git -v 1.0.0 --env-manager local -P 'hydra_options=main.env_manager=local etl.sample=sample2.csv main.experiment_name=review-release-1.0.0'
Remove-Item Env:NYC_MARK_PYTEST_FAILURE
python -m mlflow run https://github.com/mirkanodawit-source/Project-Build-an-ML-Pipeline-Starter.git -v 1.0.1 --env-manager local -P 'hydra_options=main.env_manager=local etl.sample=sample2.csv main.experiment_name=review-release-1.0.1 artifacts.model=model_export'
Remove-Item Env:PYTHONPATH
```

Run these sequentially because both use the project's `latest` data aliases.
The second command explicitly overrides the historical model name to the
rubric-required `model_export`. Keep `clean_sample.csv:reference` on sample1.
The failure flag records pytest's nonzero result as a failed W&B run, since
the old fixture does not finish its W&B run with the pytest exit code.

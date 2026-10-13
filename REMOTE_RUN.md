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
`random_forest_export` artifact with the lowest validation MAE, then run:

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

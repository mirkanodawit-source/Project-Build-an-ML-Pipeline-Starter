# Build an ML Pipeline for Short-Term Rental Prices in NYC
You are working for a property management company renting rooms and properties for short periods of 
time on various rental platforms. You need to estimate the typical price for a given property based 
on the price of similar properties. Your company receives new data in bulk every week. The model needs 
to be retrained with the same cadence, necessitating an end-to-end pipeline that can be reused.

In this project you will build such a pipeline.

## Table of contents

- [Preliminary steps](#preliminary-steps)
  * [Fork the Starter Kit](#fork-the-starter-kit)
  * [Create environment](#create-environment)
  * [Get API key for Weights and Biases](#get-api-key-for-weights-and-biases)
  * [The configuration](#the-configuration)
  * [Running the entire pipeline or just a selection of steps](#Running-the-entire-pipeline-or-just-a-selection-of-steps)
  * [Pre-existing components](#pre-existing-components)
- [Run the completed pipeline](#run-the-completed-pipeline)
  * [Release sequence](#release-sequence)
  * [Local verification](#local-verification)
- [In case of errors](#in-case-of-errors)

## Preliminary steps

### Supported Operating Systems

This project is compatible with the following operating systems:

- **Ubuntu 22.04** (Jammy Jellyfish) - both Ubuntu installation and WSL (Windows Subsystem for Linux)
- **Ubuntu 24.04** - both Ubuntu installation and WSL (Windows Subsystem for Linux)
- **macOS** - compatible with recent macOS versions

Please ensure you are using one of the supported OS versions to avoid compatibility issues.

### Python Requirement

This project requires **Python 3.13**. Please ensure that you have Python 3.13 installed and set as the default version in your environment to avoid any runtime issues.

### Fork the Starter kit
Go to [https://github.com/udacity/Project-Build-an-ML-Pipeline-Starter](https://github.com/udacity/Project-Build-an-ML-Pipeline-Starter)
and click on `Fork` in the upper right corner. This will create a fork in your Github account, i.e., a copy of the
repository that is under your control. Now clone the repository locally so you can start working on it:

```
git clone https://github.com/[your github username]/Project-Build-an-ML-Pipeline-Starter.git
```

and go into the repository:

```
cd Project-Build-an-ML-Pipeline-Starter
```
Commit and push to the repository often while you make progress towards the solution. Remember 
to add meaningful commit messages.

### Create environment
Make sure to have conda installed and ready, then create a new environment using the ``environment.yml``
file provided in the root of the repository and activate it:

```bash
> conda env create -f environment.yml
> conda activate nyc_airbnb_dev
```

### Get API key for Weights and Biases
Let's make sure we are logged in to Weights & Biases. Get your API key from W&B by going to 
[https://wandb.ai/authorize](https://wandb.ai/authorize) and click on the + icon (copy to clipboard), 
then paste your key into this command:

```bash
> wandb login [your API key]
```

You should see a message similar to:
```
wandb: Appending key for api.wandb.ai to your netrc file: /home/[your username]/.netrc
```


### The configuration
As usual, the parameters controlling the pipeline are defined in the ``config.yaml`` file defined in
the root of the starter kit. We will use Hydra to manage this configuration file. 
Open this file and get familiar with its content. Remember: this file is only read by the ``main.py`` script 
(i.e., the pipeline) and its content is
available with the ``go`` function in ``main.py`` as the ``config`` dictionary. For example,
the name of the project is contained in the ``project_name`` key under the ``main`` section in
the configuration file. It can be accessed from the ``go`` function as 
``config["main"]["project_name"]``.

NOTE: do NOT hardcode any parameter when writing the pipeline. All the parameters should be 
accessed from the configuration file.

### Running the entire pipeline or just a selection of steps
In order to run the pipeline when you are developing, you need to be in the root of the starter kit, 
then you can execute as usual:

```bash
>  mlflow run .
```
This will run the entire pipeline.

When developing it is useful to be able to run one step at the time. Say you want to run only
the ``download`` step. The `main.py` is written so that the steps are defined at the top of the file, in the 
``_steps`` list, and can be selected by using the `steps` parameter on the command line:

```bash
> mlflow run . -P steps=download
```
If you want to run the ``download`` and the ``basic_cleaning`` steps, you can similarly do:
```bash
> mlflow run . -P steps=download,basic_cleaning
```
You can override any other parameter in the configuration file using the Hydra syntax, by
providing it as a ``hydra_options`` parameter. For example, say that we want to set the parameter
modeling -> random_forest -> n_estimators to 10 and etl->min_price to 50:

```bash
> mlflow run . \
  -P steps=download,basic_cleaning \
  -P hydra_options="modeling.random_forest.n_estimators=10 etl.min_price=50"
```

### Pre-existing components
In order to simulate a real-world situation, we are providing you with some pre-implemented
re-usable components. While you have a copy in your fork, you will be using them from the original
repository by accessing them through their GitHub link, like:

```python
_ = mlflow.run(
                f"{config['main']['components_repository']}/get_data",
                "main",
                version='main',
                env_manager="conda",
                parameters={
                    "sample": config["etl"]["sample"],
                    "artifact_name": "sample.csv",
                    "artifact_type": "raw_data",
                    "artifact_description": "Raw file as downloaded"
                },
            )
```
where `config['main']['components_repository']` is set to 
[https://github.com/udacity/Project-Build-an-ML-Pipeline-Starter/tree/main/components](https://github.com/udacity/Project-Build-an-ML-Pipeline-Starter/tree/main/components).
You can see the parameters that they require by looking into their `MLproject` file:

- `get_data`: downloads the data. [MLproject](https://github.com/udacity/Project-Build-an-ML-Pipeline-Starter/blob/main/components/get_data/MLproject)
- `train_val_test_split`: segrgate the data (splits the data) [MLproject](https://github.com/udacity/Project-Build-an-ML-Pipeline-Starter/blob/main/components/train_val_test_split/MLproject)

## Run the completed pipeline

After logging in to W&B, run the first two steps to create the raw and cleaned
artifacts:

```bash
mlflow run . -P steps=download,basic_cleaning
```

In W&B, assign the `reference` alias to the first `clean_sample.csv` version.
Then validate and split the data:

```bash
mlflow run . -P steps=data_check,data_split
```

Run the four required hyperparameter combinations. Each run logs validation
`mae`, `r2`, feature importance, and a full MLflow sklearn model to W&B:

```bash
mlflow run . -P steps=train_random_forest \
  -P hydra_options="modeling.random_forest.max_depth=10,50 modeling.random_forest.n_estimators=100,200 -m"
```

Assign the `prod` alias to the `random_forest_export` artifact from the run with
the lowest validation MAE. Test that selected model on the held out test set:

```bash
mlflow run . -P steps=test_regression_model
```

The production model test is excluded from the default pipeline because it
requires that manual `prod` selection. Once the reference alias exists,
`mlflow run .` runs all other steps. Artifact names and step parameters are
defined in `config.yaml`. The `main.env_manager` setting defaults to `conda`.

### Release sequence

Tag `1.0.0` contains the complete sample1 pipeline before the NYC boundary
filter. Running it with `etl.sample=sample2.csv` exposes the out-of-area row in
`test_proper_boundaries`. Tag `1.0.1` adds the boundary filter and passes the
same data check. After publishing the tags as GitHub releases on your fork,
run each version with:

```bash
mlflow run <your-fork-git-url> -v 1.0.0 -P hydra_options="etl.sample=sample2.csv"
mlflow run <your-fork-git-url> -v 1.0.1 -P hydra_options="etl.sample=sample2.csv"
```

The `reference` alias must continue to point to the first cleaned sample;
the new `latest` alias points to the cleaned second sample.

### Local verification

The sample data and model code were checked with Python 3.13, pandas 2.3.2,
scikit-learn 1.7.2, and MLflow 3.3.2. Both samples passed all six data checks
after cleaning. Before the NYC boundary filter, sample2 had one out-of-area
listing and failed `test_proper_boundaries`, as expected.

| Data | Clean rows | Validation MAE | Test MAE |
| --- | ---: | ---: | ---: |
| sample1.csv | 19,001 | 34.18 | 33.85 |
| sample2.csv | 46,427 | 32.43 | 33.67 |

The sample1 results use 200 trees and depth 50, selected from the four
`max_depth` (10, 50) and `n_estimators` (100, 200) combinations. The default
parameters in `config.yaml` match this selection. The sample2 results use the
same parameters. These are local checks; the public W&B runs and GitHub
releases are separate rubric evidence.

## In case of errors

### Environments
When you make an error writing your `conda.yml` file, you might end up with an environment for the pipeline or one
of the components that is corrupted. Most of the time `mlflow` realizes that and creates a new one every time you try
to fix the problem. However, sometimes this does not happen, especially if the problem was in the `pip` dependencies.
In that case, you might want to clean up all conda environments created by `mlflow` and try again. In order to do so,
you can get a list of the environments you are about to remove by executing:

```
> conda info --envs | grep mlflow | cut -f1 -d" "
```

If you are ok with that list, execute this command to clean them up:

**_NOTE_**: this will remove *ALL* the environments with a name starting with `mlflow`. Use at your own risk

```
> for e in $(conda info --envs | grep mlflow | cut -f1 -d" "); do conda uninstall --name $e --all -y;done
```

This will iterate over all the environments created by `mlflow` and remove them.

### MLflow & Wandb

If you see the any error while running the command:

```
> mlflow run .
```

Please, make sure all steps are using **the same** python version and that you have **conda installed**. Additionally, *mlflow* and *wandb* packages are crucial and should have the same version.


## License

[License](LICENSE.txt)

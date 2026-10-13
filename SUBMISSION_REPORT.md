# NYC short term rental price pipeline submission report

This project implements a reusable pipeline for estimating nightly rental prices in New York City and retraining on new weekly data. MLflow coordinates data acquisition, cleaning, validation, segregation, training, and an explicitly selected production model test. Hydra supplies configuration, scikit-learn packages preprocessing with the random forest, and the artifact-backed pipeline records data and model lineage in W&B.

The core implementation and local checks are complete. Live W&B run and artifact evidence is recorded in evidence/live_audit.json. Historical release execution logs remain outstanding. Public access, training, production testing and Graph view have been verified. Local results below are labeled separately from live runs.

## Reviewer links

- GitHub repository: https://github.com/mihretupg/Project-Build-an-ML-Pipeline-Starter
- Release 1.0.0: https://github.com/mihretupg/Project-Build-an-ML-Pipeline-Starter/releases/tag/1.0.0
- Release 1.0.1: https://github.com/mihretupg/Project-Build-an-ML-Pipeline-Starter/releases/tag/1.0.1
- Public W&B project: https://wandb.ai/mirkanodawit-western-governors-university/nyc_airbnb (anonymous access verified).

## Requirement and evidence mapping

This mapping follows the attached Project Rubric.mhtml. Criterion names below match the rubric; evidence and status describe what has actually been implemented or verified.

| Rubric section | Criterion | Evidence | Status |
| --- | --- | --- | --- |
| W&B Set-Up | Public W&B project nyc_airbnb | https://wandb.ai/mirkanodawit-western-governors-university/nyc_airbnb | Anonymous project access verified; both reviewer links documented |
| Exploratory Data Analysis | Obtain sample data | evidence/live_audit.json: download_file runs | sample.csv:v0 and acquisition run verified |
| Data Cleaning | Update all parameters | src/basic_cleaning/run.py: typed CLI arguments, typed helper, parameter docstrings | Implemented |
| Data Cleaning | Run basic_cleaning without errors | evidence/live_audit.json: basic_cleaning runs | Artifact-backed cleaning run succeeded |
| Data Cleaning | Create clean_data.csv in W&B | clean_sample.csv:v0; see artifact naming clarification | clean_sample.csv:v0 verified; rubric naming discrepancy documented |
| Data Testing | Create a reference tag for the latest version of the clean_sample.csv artifact | evidence/live_audit.json: clean_sample.csv:v0 aliases | reference alias on sample1 v0 verified |
| Data Testing | Implement the test_row_count and the test_price_range tests in src/data_check/test_data.py | Both tests implemented with rubric bounds and configured prices | Implemented; shared functions pass locally |
| Data Testing | The pipeline runs successfully | evidence/live_audit.json: data_tests run mw0kho4k | Six artifact-backed pytest checks passed |
| Data Splitting | Split data into training, validation and test sets | main.py integrates train_val_test_split; train component makes validation split | Implemented; local stratified splits verified |
| Data Splitting | The pipeline again runs successfully | evidence/live_audit.json: train_val_test_split run zhsw6bpx | Successful split run and both W&B split artifacts verified |
| Train the Random Forest | Complete the src/train_random_forest/run.py script | Commented imputation/one-hot pipeline, sk_pipe, fit, MLflow save, W&B mae logging | Implemented; local full-model export and reload pass |
| Train the Random Forest | The pipeline again runs successfully | evidence/live_audit.json: finished training runs | Four required configurations completed successfully |
| Train the Random Forest | Create the model_export artifact on W&B | random_forest_export artifacts of type model_export | MLflow sklearn exports verified in W&B; artifact type model_export |
| Optimize Hyperparameters | Run training with different hyperparameters | evidence/live_audit.json; Hydra multirun | Four distinct Hydra configurations completed with MAE/R2; repeat runs also present |
| Select the Best Model | Select the best performing model and tag it as prod | Lowest validation MAE: 200 trees, depth 50; defaults match | Lowest validation MAE model v7 assigned prod |
| Test Set Verification | Verify test set performance is comparable to performance on the validation set (no overfitting) | main.py explicit test_regression_model step; local validation/test MAE table | Production artifact test succeeded: MAE 33.8469 versus validation 34.1843 |
| Visualize the Pipeline | Visualize the pipeline and verify proper structure | Artifact use/log calls establish lineage in W&B workflow | Graph view inspected; screenshot and live URL saved |
| Release the Pipeline | Release v1.0.0 of the pipeline in GitHub | evidence/live_audit.json: GitHub releases API | Release 1.0.0 public and published |
| Train the Model on a New Data Sample | Run the released pipeline on a new sample of data, with initial failure | evidence/boundary_check.json confirms shared check fails before filter | Actual tagged 1.0.0 MLflow sample2 failure log pending |
| Train the Model on a New Data Sample | Add a new cleaning step in basic_cleaning | clean_data filters NYC longitude and latitude bounds | Implemented; one sample2 outlier removed |
| Train the Model on a New Data Sample | Prepare a new release | evidence/live_audit.json: GitHub releases API | Release 1.0.1 public; subsequent Windows compatibility and evidence updates are included on main |
| Train the Model on a New Data Sample | Run the new release successfully | Both cleaned samples pass local checks; sample2 model exported | Actual tagged 1.0.1 successful MLflow run and new W&B model pending |

### Artifact naming clarification

The rubric cleaning criterion says `clean_data.csv`, but its reference criterion and the supplied step instructions say `clean_sample.csv`. This implementation uses `clean_sample.csv` consistently so reference lookup, splitting, and training agree. The rubric calls the model artifact `model_export`; the supplied instructions call it `random_forest_export`, and `model_export` is its artifact type. The implementation follows those supplied artifact names and preserves the required type. Review the names in the public W&B project before submission and flag this rubric wording discrepancy for the reviewer.

## Step 1 Exploratory data analysis

The bundled first sample contains 20,000 listings and the second contains 48,895. Exploration checks schema, descriptive statistics, missingness, neighborhood counts, and the price distribution. Outliers are excluded using the specified $10 to $350 inclusive nightly price range. Missing values remain for inference-time imputation; `last_review` is converted to datetime during cleaning. `EDA_local_executed.ipynb` contains local outputs. The original artifact-backed notebook remains available for the required W&B EDA run.

## Step 2 Cleaning and weekly data handling

The cleaning component consumes `sample.csv:latest` and logs `clean_sample.csv`. Both artifact-backed execution and local verification call the same `clean_data` function. The final cleaning rules filter price, parse review dates, and retain longitude -74.25 to -73.50 and latitude 40.5 to 41.2, inclusively. Sample1 retains 19,001 listings; sample2 retains 46,427. The sample2 boundary filter removes one out-of-area listing.

## Step 3 Data validation

Six checks verify exact column names/order, the five known borough groups, geographic boundaries, neighborhood distribution similarity, row count greater than 15,000 and less than 1,000,000, and inclusive price limits. The distribution check uses KL divergence with a configured threshold of 0.2. Sample1 is the fixed local reference for both samples. In W&B, `reference` must remain attached to the first cleaned sample while `latest` moves to sample2. Local verification calls the same six check functions; it does not claim to be an artifact-backed pytest run.

## Step 4 Training and model selection

The configured split reserves 20 percent for the held-out test set and 20 percent of the remaining data for validation. Neighborhood group stratification and seed 42 make splits reproducible. Preprocessing imputes missing values, encodes room type and borough, creates a review-date feature, and uses TF-IDF with up to five words for the listing name. All transforms and the random forest are exported together.

Models are selected using validation MAE only. Held-out test data are evaluated after selection. The search covers depths 10 and 50 crossed with 100 and 200 trees.

| Sample | Depth | Trees | Validation MAE | Validation R2 |
| --- | ---: | ---: | ---: | ---: |
| sample1.csv | 10 | 100 | 34.4319 | 0.5456 |
| sample1.csv | 10 | 200 | 34.4046 | 0.5463 |
| sample1.csv | 50 | 100 | 34.1963 | 0.5501 |
| sample1.csv | 50 | 200 | 34.1843 | 0.5506 |
| sample2.csv | 10 | 100 | 32.9430 | 0.5694 |
| sample2.csv | 10 | 200 | 32.9480 | 0.5697 |
| sample2.csv | 50 | 100 | 32.4737 | 0.5776 |
| sample2.csv | 50 | 200 | 32.4271 | 0.5781 |

Both samples select depth 50 and 200 trees. The defaults in `config.yaml` match the sample1 selection. Feature importance figures are included in `evidence/` and the local results ZIP.

## Step 5 Held out model test

The verifier saves the selected full inference pipeline in MLflow sklearn format, reloads that export, and predicts on the held-out test data. Sample1 test MAE is 0.99 percent below validation MAE; sample2 test MAE is 3.83 percent above validation MAE. These gaps are small and do not show a large held-out performance deterioration, although one split cannot rule out overfitting generally.

Predictions and models are included in `NYC-rental-pipeline-local-results.zip`.

| Sample | Clean rows | Selected validation MAE | Test MAE | Test R2 |
| --- | ---: | ---: | ---: | ---: |
| sample1.csv | 19,001 | 34.1843 | 33.8469 | 0.5619 |
| sample2.csv | 46,427 | 32.4271 | 33.6707 | 0.5726 |

The artifact-backed test uses `random_forest_export:prod` and `test_data.csv:latest`. It is intentionally excluded from the default pipeline because assigning `prod` is a manual model-selection step.

## Step 6 Release and update demonstration

Release 1.0.0 precedes the boundary fix. Release 1.0.1 includes the NYC boundary filter. Local boundary evidence demonstrates the expected failure on price-filtered sample2 and success after the filter. For the required release demonstration, run the two tagged versions on sample2 and retain the failure log from 1.0.0 and the successful pipeline log from 1.0.1. `REMOTE_RUN.md` provides the commands. A local check does not establish that the tagged MLflow pipeline was run remotely.

## Reproduction and package contents

Use Python 3.13, install `requirements-local.txt` and `pip install -e ./components`, then execute `python verify_local.py`. The script creates cleaned data, four validation comparisons per sample, selected model exports, feature importance plots, held-out predictions, and `report.json` under `artifacts/local_verification`. Move existing results aside before rerunning to preserve prior model exports.

- `SUBMISSION_REPORT.md`: this evidence narrative and requirement mapping.
- `SUBMISSION_DETAILS.txt`: text to finalize and paste into Udacity Submission Details.
- `evidence/`: local metrics, boundary checks, environment versions, and plots.
- `src/`, `components/`, MLproject files, YAML files, and sample data: executable pipeline.
- `REMOTE_RUN.md`: W&B artifact-backed run sequence without Conda.

The separate local results ZIP contains larger model exports, CSVs, and predictions. Do not upload virtual environments, API keys, private credential files, or raw browser logs.

## Submission procedure

The saved Submit Project page requires selecting a public GitHub repository. It says reviewers receive the most recent commit and need both the GitHub and public W&B URLs in the README and Submission Details. Copy the finalized local changes into the fork and commit/push them before selecting it. The ZIP is a transfer and review aid; it does not replace the required repository submission.

Source requirements: attached Project Rubric.mhtml, supplied saved course pages for Steps 1 through 6 and Submit Project; rubric link https://review.udacity.com/#!/rubrics/5155/view.

## Verified W&B execution on Windows

See evidence/live_audit.json for timestamped run states, exact artifact versions, aliases, metrics, lineage edges, anonymous project access, and public GitHub releases. evidence/wandb_model_selection.json records validation-only selection. The successful test_model run rwyfahad downloaded and evaluated the selected random_forest_export:v7 model against test_data.csv:v0.

## Completed public training and production verification

Public project: https://wandb.ai/mirkanodawit-western-governors-university/nyc_airbnb
Anonymous access verified through the W&B API.

All six artifact-backed data checks passed. Both split artifacts exist. The fixed reference is clean_sample.csv:v0. Four distinct hyperparameter configurations completed; the project contains repeated executions with the same results.

Selected model: mirkanodawit-western-governors-university/nyc_airbnb/random_forest_export:v7 (prod)
Selection run: https://wandb.ai/mirkanodawit-western-governors-university/nyc_airbnb/runs/dcmnozbd
Validation MAE: $34.1843
Validation R2: 0.5506
Held-out test run: https://wandb.ai/mirkanodawit-western-governors-university/nyc_airbnb/runs/rwyfahad
Test MAE: $33.8469
Test R2: 0.5619

Artifact graph: https://forge.coreweave.com/wandb/mirkanodawit-western-governors-university/nyc_airbnb/artifacts/model_export/random_forest_export/v7/lineage
Screenshot: evidence/wandb-pipeline-lineage.jpg

The graph confirms raw data to cleaning to splitting to training to the selected model and held-out testing. The live audit also records test-data input to the test run. The screenshot overview is compact; open the graph URL to inspect individual nodes.

Remaining submission work: execute tagged release failure/fix on sample2. The Windows-compatible source and updated documentation are included on main. Existing releases 1.0.0 and 1.0.1 are public, but their sample2 execution evidence is not yet complete. Do not submit until those items are recorded.

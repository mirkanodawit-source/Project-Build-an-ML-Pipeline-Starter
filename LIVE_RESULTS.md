# Verified public W&B results

This page preserves evidence from the first submission. For the corrected
`model_export` artifact and tagged sample2 executions, use
[SUBMISSION_REPORT.md](SUBMISSION_REPORT.md) and `SUBMISSION_DETAILS.txt`.

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

The release status above is historical; see the corrected submission report.

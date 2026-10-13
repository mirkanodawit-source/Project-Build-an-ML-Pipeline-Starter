# Verified public W&B results

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

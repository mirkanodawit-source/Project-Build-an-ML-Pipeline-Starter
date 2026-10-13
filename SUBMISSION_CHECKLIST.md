# Submission completion checklist

## Submission-page requirements

- [x] Review the rubric and map all 22 criteria to implementation and evidence.
- [ ] Complete the remaining rubric criteria, including both tagged sample2 runs.
- [x] Verify the W&B project is public (evidence/live_audit.json).
- [x] Include both the public W&B URL and GitHub repository URL in the local README.md.
- [x] Include both URLs in the prepared SUBMISSION_DETAILS.txt.
- [x] Publish the updated README, code, and evidence to the GitHub fork's main branch.
- [ ] Submit the GitHub repository link in Udacity, then paste both URLs into the actual Submission Details box.

The reviewer receives a ZIP of the repository's most recent commit. Local files
are not included until committed and pushed. The GitHub link lets the reviewer
inspect releases; the public W&B link lets them inspect runs and artifacts.
Preparing SUBMISSION_DETAILS.txt does not populate Udacity's submission form.

## Completed locally

- [x] Complete pipeline code and configuration.
- [x] Clean both samples and pass six shared data checks.
- [x] Compare four required hyperparameter combinations per sample.
- [x] Select lowest validation MAE; defaults match sample1 winner.
- [x] Export and reload complete MLflow inference models.
- [x] Test selected models on held-out data.
- [x] Include local EDA outputs, metrics, plots, and boundary failure/fix evidence.

## Complete before submitting

- [x] Satisfy the rubric EDA criterion: obtain sample data and upload sample.csv to W&B.
- [x] Run artifact-backed download and cleaning on sample1; both uploads verified through W&B API.
- [x] Set `clean_sample.csv:reference` on the first cleaned sample (verified through API).
- [x] Run W&B data checks and splitting; completed runs and both split artifacts verified.
- [x] Run four W&B training configurations; retain MAE, R2, and exports (evidence/hydra_sweep.json and evidence/live_audit.json).
- [x] Assign `prod` to the lowest-validation-MAE sample1 export.
- [x] Run the artifact-backed held-out production model test.
- [x] Capture the W&B model artifact lineage.
- [ ] Run release 1.0.0 on sample2 and save the expected boundary failure.
- [ ] Run release 1.0.1 on sample2 and save the successful full run.
- [ ] Keep the `reference` alias on sample1 during sample2 execution.
- [x] Verify anonymous access to the public W&B project.
- [ ] Replace every PENDING field in README and Submission Details with verified URLs.
- [x] Commit and push the updated source, notebook outputs, and submission documents to the public fork.
- [x] Confirm both releases are public and published on the fork.
- [x] Map all 22 criteria from the attached Project Rubric.mhtml to evidence and status.
- [ ] Verify cleaned-artifact and model-artifact naming with the reviewer-facing evidence; report documents rubric wording inconsistencies.
- [ ] Select the public GitHub repository in Udacity and paste finalized Submission Details.

The original artifact-backed EDA notebook can also be executed as additional
course evidence; the attached rubric's EDA criterion specifically requires the
sample artifact and successful acquisition. `evidence/live_audit.json` contains
the current API evidence. Historical release runs remain required: the local
boundary failure demonstration does not substitute for those runs.

# Local verification results

Models were selected using validation MAE, then reloaded from MLflow exports for held-out testing. No W&B credentials were used.

| Sample | Clean rows | Validation MAE | Test MAE | Test R2 |
| --- | ---: | ---: | ---: | ---: |
| sample1.csv | 19,001 | 34.18 | 33.85 | 0.562 |
| sample2.csv | 46,427 | 32.43 | 33.67 | 0.573 |

All six data checks passed for each sample. Sample2 contained one out-of-area listing before the boundary filter.

## Exploratory data analysis

### sample1.csv

Raw rows: 20,000. Price range: $0 to $10,000.

Missing values:

name                    7
host_name               8
last_review          4123
reviews_per_month    4123

Neighborhood counts:

neighbourhood_group
Manhattan        8774
Brooklyn         8265
Queens           2355
Bronx             441
Staten Island     165

### sample2.csv

Raw rows: 48,895. Price range: $0 to $10,000.

Missing values:

name                    16
host_name               21
last_review          10052
reviews_per_month    10052

Neighborhood counts:

neighbourhood_group
Manhattan        21661
Brooklyn         20104
Queens            5666
Bronx             1091
Staten Island      373

## Remaining submission evidence

Public W&B runs, the reference and prod aliases, and the versioned remote runs must be completed in the signed-in environment. Follow REMOTE_RUN.md.
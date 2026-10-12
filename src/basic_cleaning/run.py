#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

def go(args: argparse.Namespace) -> None:
    """Clean the raw listing artifact and upload the cleaned CSV to W&B."""

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download the input artifact and record its use in the lineage graph.
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)
    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'], errors="coerce")

    # Remove the out-of-area listing found in the second data sample.
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    # Save the cleaned data
    df.to_csv('clean_sample.csv',index=False)

    # log the new data.
    artifact = wandb.Artifact(
     args.output_artifact,
     type=args.output_type,
     description=args.output_description,
 )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)
    run.finish()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")
  
    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Raw W&B artifact to clean, including its alias or version",
        required = True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name of the cleaned output artifact",
        required = True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="W&B artifact type for the cleaned data",
        required = True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description of the cleaned output artifact",
        required = True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Lowest accepted listing price in dollars",
        required = True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Highest accepted listing price in dollars",
        required = True
    )


    args = parser.parse_args()

    go(args)

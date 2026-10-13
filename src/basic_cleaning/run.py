#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd
import tempfile


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

def clean_data(df: pd.DataFrame, min_price: float, max_price: float) -> pd.DataFrame:
    """Filter nightly prices and NYC coordinates and parse review dates.

    Args:
        df: Raw rental listings, including price, coordinates, and last_review.
        min_price: Inclusive minimum nightly price in dollars.
        max_price: Inclusive maximum nightly price in dollars.

    Returns:
        A cleaned copy with datetime review dates and valid prices and coordinates.
    """
    df = df[df['price'].between(min_price, max_price)].copy()
    df['last_review'] = pd.to_datetime(df['last_review'], errors="coerce")
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    return df[idx].copy()

def go(args: argparse.Namespace) -> None:
    """Clean the raw listing artifact and upload the cleaned CSV to W&B.

    Args:
        args: Parsed CLI parameters. input_artifact, output_artifact, output_type,
            and output_description are strings; min_price and max_price are floats.
    """

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download the input artifact and record its use in the lineage graph.
    artifact_local_path = run.use_artifact(args.input_artifact).file(root=tempfile.mkdtemp(prefix="nyc-raw-"))
    df = pd.read_csv(artifact_local_path)
    df = clean_data(df, args.min_price, args.max_price)

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

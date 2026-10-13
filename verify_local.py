"""Verify bundled data and export models without W&B credentials or Conda."""
import json
from pathlib import Path
import sys

import mlflow.sklearn
import pandas as pd
import yaml
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src" / "train_random_forest"))
from run import get_inference_pipeline, plot_feature_importance
from src.basic_cleaning.run import clean_data
from src.data_check import test_data as checks


def main():
    config = yaml.safe_load((ROOT / "config.yaml").read_text())
    etl, modeling = config["etl"], config["modeling"]
    output = ROOT / "artifacts" / "local_verification"
    output.mkdir(parents=True, exist_ok=True)
    report = {"config": config, "samples": {}}
    reference = None
    for sample in ("sample1.csv", "sample2.csv"):
        raw = pd.read_csv(ROOT / "components" / "get_data" / "data" / sample)
        data = clean_data(raw, etl["min_price"], etl["max_price"])
        # Round-trip the CSV, as the W&B data checks do.
        sample_dir = output / Path(sample).stem
        sample_dir.mkdir(exist_ok=True)
        data.to_csv(sample_dir / "clean_sample.csv", index=False)
        data = pd.read_csv(sample_dir / "clean_sample.csv")
        if reference is None:
            reference = data
        checks.test_column_names(data)
        checks.test_neighborhood_names(data)
        checks.test_proper_boundaries(data)
        checks.test_similar_neigh_distrib(data, reference, config["data_check"]["kl_threshold"])
        checks.test_row_count(data)
        checks.test_price_range(data, etl["min_price"], etl["max_price"])
        before_boundary = raw[raw.price.between(etl["min_price"], etl["max_price"])]
        out_of_area = int((~(before_boundary.longitude.between(-74.25, -73.50)
                            & before_boundary.latitude.between(40.5, 41.2))).sum())
        stratify = modeling["stratify_by"]
        def split(frame, size):
            return train_test_split(frame, test_size=size, random_state=modeling["random_seed"],
                                    stratify=frame[stratify] if stratify != "none" else None)
        trainval, test = split(data, modeling["test_size"])
        train, val = split(trainval, modeling["val_size"])
        trainval.to_csv(sample_dir / "trainval_data.csv", index=False)
        test.to_csv(sample_dir / "test_data.csv", index=False)
        candidates = []
        best = None
        for depth in (10, 50):
            for trees in (100, 200):
                params = dict(modeling["random_forest"], max_depth=depth,
                              n_estimators=trees, random_state=modeling["random_seed"])
                pipe, names = get_inference_pipeline(params, modeling["max_tfidf_features"])
                pipe.fit(train.drop(columns="price"), train.price)
                pred = pipe.predict(val.drop(columns="price"))
                metrics = {"max_depth": depth, "n_estimators": trees,
                           "validation_mae": float(mean_absolute_error(val.price, pred)),
                           "validation_r2": float(r2_score(val.price, pred))}
                candidates.append(metrics)
                print(sample, metrics, flush=True)
                if best is None or metrics["validation_mae"] < best[0]["validation_mae"]:
                    best = metrics, pipe, names
        metrics, pipe, names = best
        model_dir = sample_dir / "model"
        if model_dir.exists():
            raise FileExistsError(f"Preserving existing export: {model_dir}; move it before rerunning")
        example = train.drop(columns="price").iloc[:5].copy()
        cols = example.select_dtypes(include="integer").columns
        example[cols] = example[cols].astype(float)
        mlflow.sklearn.save_model(pipe, str(model_dir), input_example=example)
        loaded = mlflow.sklearn.load_model(str(model_dir))
        predictions = loaded.predict(test.drop(columns="price"))
        pd.DataFrame({"actual_price": test.price, "predicted_price": predictions}).to_csv(
            sample_dir / "test_predictions.csv", index=False)
        fig = plot_feature_importance(pipe, names)
        fig.savefig(sample_dir / "feature_importance.png")
        import matplotlib.pyplot as plt
        plt.close(fig)
        report["samples"][sample] = {
            "raw_rows": len(raw), "clean_rows": len(data), "data_checks_passed": 6,
            "out_of_area_before_filter": out_of_area, "candidates": candidates,
            "selected": metrics, "test_mae": float(mean_absolute_error(test.price, predictions)),
            "test_r2": float(r2_score(test.price, predictions)),
        }
        (output / "report.json").write_text(json.dumps(report, indent=2))
    print(f"Verified both samples. Report: {output / 'report.json'}", flush=True)


if __name__ == "__main__":
    main()

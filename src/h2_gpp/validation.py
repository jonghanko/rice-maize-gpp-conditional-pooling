"""Independent arithmetic checks on public aggregate files, using the standard library."""

import hashlib
import json
import math
import statistics
from pathlib import Path


INPUT_NAMES = (
    "SCORES.json", "ALL_CONTRASTS.json", "SEASON_SUMMARY.json",
    "CROSS_AXIS_SIGNS.json", "FIGURE_SOURCE.json", "TABLE_SOURCE.json",
)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(actual, expected, label):
    require(math.isfinite(actual) and math.isfinite(expected), label + ": nonfinite value")
    require(math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-10),
            f"{label}: {actual!r} differs from {expected!r}")


def select_one(records, **keys):
    matches = [record for record in records
               if all(record.get(key) == value for key, value in keys.items())]
    require(len(matches) == 1, f"Expected one aggregate record for {keys}, found {len(matches)}")
    return matches[0]


def verify_inputs(data_dir):
    """Verify hashes and relationships among stored aggregates; never load models."""
    data_dir = Path(data_dir).resolve()
    manifest = load_json(data_dir / "INPUT_MANIFEST.json")
    expected_names = set(INPUT_NAMES)
    require(set(manifest["files"]) == expected_names, "Unexpected public aggregate input list")
    for name, expected_hash in manifest["files"].items():
        require(sha256(data_dir / name) == expected_hash, "Input checksum mismatch: " + name)

    scores = load_json(data_dir / "SCORES.json")
    contrasts = load_json(data_dir / "ALL_CONTRASTS.json")
    summaries = load_json(data_dir / "SEASON_SUMMARY.json")
    recurrence = load_json(data_dir / "CROSS_AXIS_SIGNS.json")
    figures = load_json(data_dir / "FIGURE_SOURCE.json")
    metrics = scores["metrics"]
    macro = scores["macro_region_rmse"]
    require(len(metrics) == 456 and len(macro) == 24, "Aggregate metric dimensions changed")
    require(len(contrasts) == 444 and len(summaries) == 24, "Post hoc dimensions changed")

    for row in macro:
        regions = [item for item in metrics
                   if item["level"] == "region"
                   and all(item[key] == row[key] for key in ("axis", "family", "crop", "arm"))]
        require(len(regions) == row["regions"] == 3, "Regional macro denominator")
        close(statistics.mean(item["rmse"] for item in regions), row["rmse"], "Regional macro RMSE")

    for row in scores["crop_contrasts"]:
        arm, reference = row["contrast"].split("-")
        keys = {key: row[key] for key in ("axis", "family", "crop")}
        arm_rmse = select_one(macro, **keys, arm=arm)["rmse"]
        reference_rmse = select_one(macro, **keys, arm=reference)["rmse"]
        close(row["rmse_arm"], arm_rmse, "Crop macro arm")
        close(row["rmse_reference"], reference_rmse, "Crop macro reference")
        close(row["delta_percent"], 100 * (arm_rmse / reference_rmse - 1), "Crop macro contrast")

    for row in scores["overall_contrasts"]:
        crops = [item["delta_percent"] for item in scores["crop_contrasts"]
                 if all(item[key] == row[key] for key in ("axis", "family", "contrast"))]
        require(len(crops) == 2, "Equal-crop denominator")
        close(row["equal_crop_relative_delta_percent"], statistics.mean(crops), "Equal-crop contrast")

    grouping = {
        "crop": ("axis", "family", "crop"),
        "region": ("axis", "family", "crop", "spatial_split_group"),
        "site_season": ("axis", "family", "crop", "site_id", "year"),
    }
    for row in contrasts:
        arm, reference = row["contrast"].split("-")
        keys = {key: row[key] for key in grouping[row["level"]]}
        first = select_one(metrics, level=row["level"], arm=arm, **keys)
        second = select_one(metrics, level=row["level"], arm=reference, **keys)
        require(first["n"] == second["n"] == row["n"], "Paired aggregate count")
        close(row["rmse_arm"], first["rmse"], "Paired arm RMSE")
        close(row["rmse_ref"], second["rmse"], "Paired reference RMSE")
        close(row["relative_percent"], 100 * (first["rmse"] / second["rmse"] - 1), "Paired percent")
        close(row["delta_rmse"], first["rmse"] - second["rmse"], "Paired RMSE difference")
        close(row["delta_mse"], first["rmse"] ** 2 - second["rmse"] ** 2, "MSE difference")
        close(row["delta_sse"], row["delta_mse"] * row["n"], "SSE difference")
        close(row["delta_squared_bias"], first["bias"] ** 2 - second["bias"] ** 2, "Bias term")
        close(row["delta_mse"], row["delta_squared_bias"] + row["delta_centered_error_variance"],
              "MSE decomposition")
        close(row["mae_arm"], first["mae"], "Paired arm MAE")
        close(row["mae_ref"], second["mae"], "Paired reference MAE")
        require(row["worse_rmse"] == (first["rmse"] > second["rmse"]), "Adverse RMSE sign")
        require(row["worse_mae"] == (first["mae"] > second["mae"]), "Adverse MAE sign")

    seasons = [row for row in contrasts if row["level"] == "site_season"]
    for summary in summaries:
        group = [row for row in seasons
                 if all(row[key] == summary[key] for key in ("axis", "family", "crop", "contrast"))]
        require(len(group) == summary["seasons"], "Site-season summary denominator")
        for metric in ("rmse", "mae"):
            require(sum(row["worse_" + metric] for row in group) == summary["adverse_" + metric],
                    "Adverse count: " + metric)
        close(statistics.median(row["relative_percent"] for row in group),
              summary["median_relative_percent"], "Site-season median")

    for record in recurrence:
        by_axis = []
        for axis in ("cluster_loso", "year_loyo"):
            by_axis.append({f"{row['site_id']}:{row['year']}" for row in seasons
                            if row["axis"] == axis and row["worse_rmse"]
                            and all(row[key] == record[key] for key in ("family", "crop", "contrast"))})
        require(sorted(by_axis[0] & by_axis[1]) == sorted(record["both_keys"]), "Cross-axis recurrence")

    for row in figures["figure1"]:
        expected = select_one(scores["crop_contrasts"],
                              **{key: row[key] for key in ("axis", "family", "crop", "contrast")})
        require(row == expected, "Figure 1 source point")
    figure2 = figures["figure2"]
    require(len(figure2["row_keys"]) == 29 and len(figure2["column_keys"]) == 4, "Figure 2 dimensions")
    for row_index, (crop, site, year) in enumerate(figure2["row_keys"]):
        for column_index, (axis, family) in enumerate(figure2["column_keys"]):
            row = select_one(seasons, crop=crop, site_id=site, year=year, axis=axis,
                             family=family, contrast="C-S")
            close(figure2["relative_percent"][row_index][column_index],
                  row["relative_percent"], "Figure 2 source cell")

    primary = select_one(scores["overall_contrasts"], axis="cluster_loso", family="Ridge", contrast="C-S")
    close(primary["equal_crop_relative_delta_percent"], 0.18150003401997683, "Prespecified primary contrast")
    return {
        "status": "PASS",
        "scope": "Archived aggregate arithmetic and input checksums",
        "input_hashes": {name: sha256(data_dir / name) for name in INPUT_NAMES},
        "metric_rows": len(metrics), "regional_macro_rows": len(macro),
        "paired_contrasts": len(contrasts), "season_summaries": len(summaries),
        "figure1_points": len(figures["figure1"]), "figure2_cells": 116,
        "primary_Ridge_LOSO_C_minus_S_percent": primary["equal_crop_relative_delta_percent"],
        "new_fits": 0, "new_predictions": 0, "model_replays": 0,
        "ET_training_hold": True, "Germany_training_hold": True,
    }

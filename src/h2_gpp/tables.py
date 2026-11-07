"""Render the approved H2 tables from archived aggregate JSON records.

This module does not read observations, model objects or prediction records.
Importing it performs no file operations. Call :func:`render_tables` explicitly.
"""

from __future__ import annotations

import csv
import html
import io
import json
import math
import os
from pathlib import Path
import tempfile


_AXES = (("cluster_loso", "LOSO"), ("year_loyo", "LOYO"))
_FAMILIES = ("Ridge", "RF")
_CROPS = ("rice", "maize")

_TABLE_1 = {
    "name": "Table_1_v0_2",
    "caption": (
        "Table 1. Fixed model recipes and outer validation design for daily GPP "
        "prediction."
    ),
    "headers": ["Arm", "Ridge", "Random forest", "Training weight per row"],
    "rows": [
        [
            "Crop-specific (S)",
            "Separate models with 8 inputs per crop",
            "Separate models with 8 inputs per crop",
            "1",
        ],
        [
            "Unconditioned pooling (P)",
            "One pooled model with 8 inputs",
            "One pooled model with 8 inputs",
            "n / (2 × n_crop)",
        ],
        [
            "Crop-conditioned pooling (C)",
            "One pooled model with 17 columns (8 scaled inputs, crop indicator, "
            "8 interactions)",
            "One pooled model with 9 columns (8 physical inputs and crop indicator)",
            "n / (2 × n_crop)",
        ],
    ],
    "note": (
        "Here n is the total number of outer-training site-days in the fold and "
        "n_crop is the number for the row’s crop. Ridge uses α = 10, the singular "
        "value decomposition solver, an unpenalized intercept, and training-only "
        "population scaling with the same weights used for fitting. The random "
        "forest settings are 200 bootstrapped trees, a minimum of five samples "
        "per leaf, all predictors eligible at each split, seed 42, and one "
        "estimator thread. Each fold required at least 300 training site-days "
        "per crop. The GPP analysis used 4,357 site-days, six spatial-cluster "
        "holdouts, nine year holdouts, and 120 fitted estimators. Model fitting "
        "for ET and for German data remained on hold."
    ),
}

_TABLE_2 = {
    "name": "Table_2_v0_2",
    "caption": (
        "Table 2. Within-crop equal-region RMSE and changes relative to "
        "crop-specific fitting."
    ),
    "headers": ["Axis", "Model", "Crop", "S", "P", "C", "P−S (%)", "C−S (%)"],
    "note": (
        "Root mean squared error (RMSE) is in g C m⁻² d⁻¹ and is displayed to "
        "four decimal places. Each within-crop score gives equal weight to the "
        "RMSEs for that crop’s three spatial clusters. For year holdout, "
        "out-of-fold site-days from the held-out years are combined within each "
        "spatial cluster before computing its RMSE. P−S and C−S are 100 × "
        "(arm RMSE / S RMSE − 1), using the unrounded within-crop scores. "
        "Percentages are displayed to two decimal places. Positive values "
        "indicate higher RMSE. S denotes crop-specific fitting, P unconditioned "
        "pooling, and C crop-conditioned pooling. LOSO denotes "
        "leave-one-spatial-cluster-out, LOYO denotes leave-one-year-out, and RF "
        "denotes random forest."
    ),
}

_TABLE_3 = {
    "name": "Table_3_v0_2",
    "caption": (
        "Table 3. Counts of site-seasons with adverse errors under each pooling "
        "comparison."
    ),
    "headers": [
        "Axis", "Model", "Crop", "Site-seasons (n)", "P−S (RMSE)",
        "C−S (RMSE)", "C−P (RMSE)", "C−S (MAE)",
    ],
    "note": (
        "The denominator for each row is all retained site-year subsets for "
        "that crop, 14 for rice and 15 for maize. The four error columns count "
        "site-seasons where the first arm’s unrounded error strictly exceeded "
        "the comparator’s on the same site-days. S is the comparator for P−S "
        "and C−S, and P is the comparator for C−P. The counts are post hoc and "
        "use a strict increase in error as the cutoff. RMSE denotes root mean "
        "squared error and MAE denotes mean absolute error. S denotes "
        "crop-specific fitting, P unconditioned pooling, and C crop-conditioned "
        "pooling. LOSO denotes leave-one-spatial-cluster-out, LOYO denotes "
        "leave-one-year-out, and RF denotes random forest."
    ),
}

_TABLE_S1 = {
    "name": "Supplementary_Table_S1_v0_1",
    "caption": (
        "Supplementary Table S1. Paired site-season RMSE values underlying "
        "Figure 2."
    ),
    "headers": [
        "Crop", "Site", "Year", "Validation", "Model", "Paired site-days (n)",
        "S RMSE", "C RMSE", "C−S (%)",
    ],
    "note": (
        "Each row covers one retained site-year subset, model family, and "
        "validation axis. Root mean squared error (RMSE) is in g C m⁻² d⁻¹. "
        "S denotes crop-specific fitting and C denotes crop-conditioned "
        "pooling. Both RMSEs use the same n site-days. Relative change is "
        "100 × (C RMSE / S RMSE − 1). A positive value indicates higher RMSE "
        "for C. Values are shown at the precision stored in the archive. "
        "Figure 2 displays the relative changes to one decimal place. LOSO "
        "denotes leave-one-spatial-cluster-out, LOYO denotes leave-one-year-out, "
        "and RF denotes random forest."
    ),
}


def _load_json(data_dir: Path, filename: str):
    with (data_dir / filename).open(encoding="utf-8-sig") as stream:
        return json.load(stream)


def _index(records: list[dict], fields: tuple[str, ...]) -> dict[tuple, dict]:
    indexed = {}
    for record in records:
        key = tuple(record[field] for field in fields)
        if key in indexed:
            raise ValueError(f"Duplicate aggregate record for {fields}: {key}")
        indexed[key] = record
    return indexed


def _signed(value: float, precision: int | None = None) -> str:
    if not math.isfinite(value):
        raise ValueError("A table percentage must be finite")
    text = format(value, "+" if precision is None else f"+.{precision}f")
    return text.replace("-", "−", 1)


def _table_2_rows(scores: dict) -> list[list[str]]:
    metrics = _index(
        scores["macro_region_rmse"], ("axis", "family", "crop", "arm")
    )
    contrasts = _index(
        scores["crop_contrasts"], ("axis", "family", "crop", "contrast")
    )
    rows = []
    for axis, label in _AXES:
        for family in _FAMILIES:
            for crop in _CROPS:
                key = (axis, family, crop)
                values = [metrics[(*key, arm)]["rmse"] for arm in ("S", "P", "C")]
                if not all(math.isfinite(value) for value in values):
                    raise ValueError(f"Nonfinite regional RMSE in {key}")
                rows.append([
                    label, family, crop,
                    *(f"{value:.4f}" for value in values),
                    _signed(contrasts[(*key, "P-S")]["delta_percent"], 2),
                    _signed(contrasts[(*key, "C-S")]["delta_percent"], 2),
                ])
    return rows


def _table_3_rows(summary: list[dict]) -> list[list[str]]:
    records = _index(summary, ("axis", "family", "crop", "contrast"))
    rows = []
    for axis, label in _AXES:
        for family in _FAMILIES:
            for crop in _CROPS:
                key = (axis, family, crop)
                specific = records[(*key, "C-S")]
                count = specific["seasons"]
                expected = 14 if crop == "rice" else 15
                if count != expected:
                    raise ValueError(f"Site-season denominator differs from the approved table: {key}")
                rows.append([
                    label, family, crop, str(count),
                    str(records[(*key, "P-S")]["adverse_rmse"]),
                    str(specific["adverse_rmse"]),
                    str(records[(*key, "C-P")]["adverse_rmse"]),
                    str(specific["adverse_mae"]),
                ])
    return rows


def _table_s1_rows(contrasts: list[dict]) -> list[list[str]]:
    records = [
        record for record in contrasts
        if record["level"] == "site_season" and record["contrast"] == "C-S"
    ]
    _index(records, ("crop", "site_id", "year", "axis", "family"))
    if len(records) != 116:
        raise ValueError("The approved supplementary table requires 116 paired records")
    axis_order = {axis: index for index, (axis, _) in enumerate(_AXES)}
    records.sort(key=lambda record: (
        _CROPS.index(record["crop"]), record["site_id"], record["year"],
        axis_order[record["axis"]], _FAMILIES.index(record["family"]),
    ))
    labels = dict(_AXES)
    rows = []
    for record in records:
        if not all(math.isfinite(record[key]) for key in ("rmse_ref", "rmse_arm")):
            raise ValueError("A supplementary RMSE must be finite")
        rows.append([
            record["crop"], record["site_id"], str(record["year"]),
            labels[record["axis"]], record["family"], str(record["n"]),
            str(record["rmse_ref"]), str(record["rmse_arm"]),
            _signed(record["relative_percent"]),
        ])
    return rows


def _csv_text(headers: list[str], rows: list[list[str]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return stream.getvalue()


def _markdown_text(table: dict) -> str:
    lines = [table["caption"], "", "| " + " | ".join(table["headers"]) + " |"]
    lines.append("| " + " | ".join("---" for _ in table["headers"]) + " |")
    lines.extend("| " + " | ".join(row) + " |" for row in table["rows"])
    return "\n".join([*lines, "", table["note"], ""])


def _html_text(table: dict) -> str:
    caption = html.escape(table["caption"])
    headers = "".join(f"<th>{html.escape(cell)}</th>" for cell in table["headers"])
    rows = [
        "    <tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row) + "</tr>"
        for row in table["rows"]
    ]
    return "\n".join([
        '<!DOCTYPE html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
        f"<title>{caption}</title>", "<style>",
        "body { font: 12pt Arial, sans-serif; margin: 32px; max-width: 1150px; }",
        "h1 { font-size: 14pt; font-weight: normal; font-style: normal; }",
        "table { border-collapse: collapse; border-top: 1pt solid black; "
        "border-bottom: 1pt solid black; width: 100%; }",
        "thead { border-bottom: 1pt solid black; display: table-header-group; }",
        "th, td { border: 0; font-size: 12pt; font-weight: normal; font-style: normal; "
        "padding: 7px; text-align: left; vertical-align: top; }",
        "</style>", "</head>", "<body>", f"<h1>{caption}</h1>", "<table>",
        "  <thead>", f"    <tr>{headers}</tr>", "  </thead>", "  <tbody>",
        *rows, "  </tbody>", "</table>", f"<p>{html.escape(table['note'])}</p>",
        "</body>", "</html>", "",
    ])


def render_tables(data_dir: str | Path, output_dir: str | Path) -> list[Path]:
    """Write the approved four tables in CSV, Markdown and HTML formats.

    ``data_dir`` contains ``SCORES.json``, ``SEASON_SUMMARY.json`` and
    ``ALL_CONTRASTS.json``. No source-project paths are used. All inputs and
    rendered contents are validated before output files are replaced. Each
    individual replacement is atomic, and repeated calls are deterministic.
    The returned paths identify the twelve generated files.
    """
    data_dir = Path(data_dir)
    output_dir = Path(output_dir)
    scores = _load_json(data_dir, "SCORES.json")
    summary = _load_json(data_dir, "SEASON_SUMMARY.json")
    contrasts = _load_json(data_dir, "ALL_CONTRASTS.json")
    tables = [
        _TABLE_1,
        {**_TABLE_2, "rows": _table_2_rows(scores)},
        {**_TABLE_3, "rows": _table_3_rows(summary)},
        {**_TABLE_S1, "rows": _table_s1_rows(contrasts)},
    ]
    artifacts = {}
    for table in tables:
        artifacts[f"{table['name']}.csv"] = _csv_text(table["headers"], table["rows"])
        artifacts[f"{table['name']}.md"] = _markdown_text(table)
        artifacts[f"{table['name']}.html"] = _html_text(table)

    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".h2-tables-", dir=output_dir) as temporary:
        staging_dir = Path(temporary)
        for name, content in artifacts.items():
            (staging_dir / name).write_text(content, encoding="utf-8", newline="\n")
        for name in artifacts:
            os.replace(staging_dir / name, output_dir / name)
    return [output_dir / name for name in artifacts]

"""Render the approved 180 mm H2 figures from aggregate results only.

This module never loads observations, fitted models, or row-level predictions.
Importing it does not read or write files.  The layout follows the final
submission TIFF renderer; rendering is an explicit call to ``render_figures``.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import re
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

import matplotlib as mpl
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import TwoSlopeNorm
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties, findfont
from matplotlib.lines import Line2D
import numpy as np
from PIL import Image


WIDTH_MM = 180
DPI = 600
FONT_PT = 12.2
POINTS_PER_MM = 72 / 25.4
PLOT_TEXT = "#1b252d"
GRID = "#dbe1e5"
AXES = ("cluster_loso", "year_loyo")
CATEGORIES = (("Ridge", "rice"), ("Ridge", "maize"), ("RF", "rice"), ("RF", "maize"))
CONTRASTS = {"P-S": ("#b24322", "o", -0.16), "C-S": ("#176785", "s", 0.16)}
PITCH = 15.4
HEADER = 38

FINAL_CAPTIONS = """Figure 1. Relative changes in within-crop regional macro root mean squared error (RMSE) compared with crop-specific fitting (S). Panels (A) and (B) show spatial-cluster holdout and year holdout, respectively. Each within-crop score is the equally weighted mean of the out-of-fold RMSEs for that crop’s three spatial clusters. In panel (B), each cluster RMSE pools site-days across held-out years. Points show 100 × (arm RMSE / S RMSE − 1) from the unrounded within-crop scores for unconditioned pooling (P) and crop-conditioned pooling (C). Positive values indicate higher RMSE. RF denotes random forest. The points are descriptive estimates shown without uncertainty intervals. See Table 1 for the model recipes and Table 2 for the displayed scores.

Figure 2. Post hoc relative changes in site-season root mean squared error (RMSE) for crop-conditioned pooling (C) versus crop-specific fitting (S). Each cell shows 100 × (C RMSE / S RMSE − 1) for the indicated model family and validation axis, with both RMSEs computed over the same retained site-days. Panel (A) shows rice (14 site-seasons), and panel (B) shows maize (15 site-seasons). LOSO denotes leave-one-spatial-cluster-out, LOYO denotes leave-one-year-out, and RF denotes random forest. Red indicates higher RMSE for C and blue indicates lower RMSE. Both blocks share a color scale from −12% to +12% based on unrounded changes. Cell labels are rounded to one decimal place. Signed zeros indicate small changes that rounded to zero. Supplementary Table S1 gives the paired site-day counts, both arm RMSEs, and relative changes at the precision stored in the archive. The same retained site-years are evaluated on both axes.
"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_aggregates(data_dir: Path) -> tuple[dict, dict, dict, list, dict]:
    sources = {}
    payloads = {}
    for name in ("FIGURE_SOURCE.json", "SCORES.json", "ALL_CONTRASTS.json"):
        path = data_dir / name
        raw = path.read_bytes()
        sources[name] = hashlib.sha256(raw).hexdigest()
        payloads[name] = json.loads(raw.decode("utf-8-sig"))
    figure = payloads["FIGURE_SOURCE.json"]
    scores = payloads["SCORES.json"]
    contrasts = payloads["ALL_CONTRASTS.json"]
    points = {}
    expected = {(axis, family, crop, contrast) for axis in AXES
                for family, crop in CATEGORIES for contrast in CONTRASTS}
    macro = {(r["axis"], r["family"], r["crop"], r["arm"]): r["rmse"]
             for r in scores["macro_region_rmse"]}
    score_contrasts = {(r["axis"], r["family"], r["crop"], r["contrast"]): r
                       for r in scores["crop_contrasts"]}
    for row in figure["figure1"]:
        key = tuple(row[k] for k in ("axis", "family", "crop", "contrast"))
        _require(key not in points and key in expected, f"Unexpected/duplicate Figure 1 key: {key}")
        value = row["delta_percent"]
        _require(math.isfinite(value), f"Nonfinite Figure 1 value: {key}")
        _require(value == score_contrasts[key]["delta_percent"], f"Figure 1 contrast mismatch: {key}")
        arm = key[3][0]
        reference = macro[key[:3] + ("S",)]
        arm_value = macro[key[:3] + (arm,)]
        _require(reference > 0 and row["rmse_reference"] == reference and row["rmse_arm"] == arm_value,
                 f"Figure 1 S/P/C score mismatch: {key}")
        _require(math.isclose(value, 100 * (arm_value / reference - 1), rel_tol=0, abs_tol=1e-12),
                 f"Figure 1 ratio mismatch: {key}")
        points[key] = value
    _require(set(points) == expected, "Figure 1 must contain the 16 prescribed contrasts")
    grid = figure["figure2"]
    matrix = np.asarray(grid["relative_percent"], dtype=float)
    _require(matrix.shape == (29, 4) and bool(np.isfinite(matrix).all()), "Figure 2 needs a finite 29 by 4 matrix")
    _require(grid["color_bound"] == 12, "The approved Figure 2 color bound is 12 percent")
    _require(grid["column_keys"] == [["cluster_loso", "Ridge"], ["cluster_loso", "RF"],
                                    ["year_loyo", "Ridge"], ["year_loyo", "RF"]], "Figure 2 column order changed")
    row_keys = [tuple(row) for row in grid["row_keys"]]
    _require(len(row_keys) == len(set(row_keys)) == 29, "Figure 2 site-season keys must be unique")
    _require(sum(row[0] == "rice" for row in row_keys) == 14 and
             sum(row[0] == "maize" for row in row_keys) == 15, "Figure 2 crop denominators changed")
    _require(row_keys == sorted(row_keys, key=lambda r: (0 if r[0] == "rice" else 1, r[1], r[2])),
             "Figure 2 approved row order changed")
    seasons = {}
    for row in contrasts:
        if row["level"] == "site_season" and row["contrast"] == "C-S":
            key = tuple(row[k] for k in ("crop", "site_id", "year", "axis", "family"))
            _require(key not in seasons, f"Duplicate site-season contrast: {key}")
            seasons[key] = row
    _require(len(seasons) == 116, "Expected 116 archived site-season C-S contrasts")
    for i, row in enumerate(row_keys):
        for j, column in enumerate(grid["column_keys"]):
            key = row + tuple(column)
            record = seasons[key]
            _require(matrix[i, j] == record["relative_percent"], f"Figure 2 value mismatch: {key}")
            _require(record["n"] > 0 and record["rmse_ref"] > 0, f"Invalid paired summary: {key}")
            _require(math.isclose(matrix[i, j], 100 * (record["rmse_arm"] / record["rmse_ref"] - 1),
                                  rel_tol=0, abs_tol=1e-12), f"Figure 2 ratio mismatch: {key}")
    return figure, points, sources, contrasts, seasons


class _Canvas:
    def __init__(self, height_pt: float):
        self.width = WIDTH_MM * POINTS_PER_MM
        self.height = height_pt
        self.figure = Figure(figsize=(self.width / 72, self.height / 72), dpi=144, facecolor="white")
        FigureCanvasAgg(self.figure)
        self.text_boxes = []

    def text(self, x, y, label, *, ha="center", size=FONT_PT, weight="normal", color=PLOT_TEXT, region=None):
        artist = self.figure.text(x / self.width, 1 - y / self.height, label, ha=ha, va="center",
                                  fontsize=size, fontweight=weight, color=color)
        self.text_boxes.append((artist, region))
        return artist

    def axes(self, left, top, width, height):
        ax = self.figure.add_axes([left / self.width, 1 - (top + height) / self.height,
                                   width / self.width, height / self.height])
        ax.set_axis_off()
        return ax

    def marker(self, x, y, color, style):
        self.figure.add_artist(Line2D([x / self.width], [1 - y / self.height], transform=self.figure.transFigure,
                                      linestyle="none", marker=style, color=color, markeredgecolor="none", markersize=6.8))

    def audit(self):
        self.figure.canvas.draw()
        renderer = self.figure.canvas.get_renderer()
        scale = 72 / self.figure.dpi
        spans = []
        for artist, region in self.text_boxes:
            box = artist.get_window_extent(renderer)
            x0, x1 = box.x0 * scale, box.x1 * scale
            y0, y1 = self.height - box.y1 * scale, self.height - box.y0 * scale
            label = artist.get_text()
            _require(artist.get_fontsize() >= FONT_PT, f"Font below {FONT_PT} pt: {label}")
            _require(x0 >= 1 and y0 >= 1 and x1 <= self.width - 1 and y1 <= self.height - 1,
                     f"Text outside canvas: {label}")
            if region:
                left, top, right, bottom = region
                _require(x0 >= left and x1 <= right and y0 >= top and y1 <= bottom,
                         f"Text outside assigned cell: {label}")
            spans.append((label, x0, y0, x1, y1))
        for (a, ax0, ay0, ax1, ay1), (b, bx0, by0, bx1, by1) in itertools.combinations(spans, 2):
            _require(min(ax1, bx1) - max(ax0, bx0) <= 0 or min(ay1, by1) - max(ay0, by0) <= 0,
                     f"Overlapping text: {a}; {b}")
        return {"text_labels": len(spans), "min_font_pt": min(a.get_fontsize() for a, _ in self.text_boxes),
                "overlap_count": 0, "outside_canvas_count": 0,
                "min_frame_margin_pt": round(min(min(x0, y0, self.width-x1, self.height-y1)
                                                   for _, x0, y0, x1, y1 in spans), 2)}


def _figure1(points):
    canvas = _Canvas(184)
    width = (canvas.width - 84 - 21 - 7) / 2
    mapping = []
    for panel, axis in enumerate(AXES):
        left, top, height = 84 + panel * (width + 21), 28, 91
        ax = canvas.axes(left, top, width, height)
        ax.set_xlim(-5, 45)
        ax.set_ylim(3.5, -.5)
        canvas.text(left, top - 12, f"({'AB'[panel]})", ha="left", size=14, weight="bold")
        for tick in (0, 10, 20, 30, 40):
            ax.vlines(tick, -.5, 3.5, color="#69747b" if tick == 0 else GRID, linewidth=2, zorder=1)
            ax.vlines(tick, 3.36, 3.5, color="#46525b", linewidth=2)
            canvas.text(left + (tick + 5) / 50 * width, top + height + 10, str(tick))
        ax.hlines(3.5, -5, 45, color="#46525b", linewidth=2, clip_on=False)
        for row, (model, crop) in enumerate(CATEGORIES):
            if panel == 0:
                canvas.text(left - 6, top + (row + .5) / 4 * height, f"{model} / {crop.title()}", ha="right")
            for contrast, (color, marker, offset) in CONTRASTS.items():
                value = points[(axis, model, crop, contrast)]
                ax.plot(value, row + offset, marker=marker, linestyle="none", markersize=6.6,
                        color=color, markeredgecolor="none", zorder=3)
                mapping.append({"axis": axis, "family": model, "crop": crop, "contrast": contrast,
                                "delta_percent": value, "marker": marker, "color": color,
                                "x_pt": left + (value + 5) / 50 * width,
                                "y_pt": top + (row + offset + .5) / 4 * height})
    cx = canvas.width / 2
    canvas.text(cx, canvas.height - 38, "Regional macro RMSE change (%)")
    for dx, (contrast, (color, marker, _)) in zip((-53, 14), CONTRASTS.items()):
        canvas.marker(cx + dx, canvas.height - 15, color, marker)
        canvas.text(cx + dx + 9, canvas.height - 15, contrast.replace("-", "−"), ha="left")
    return canvas, mapping


def _cell_ink(value, colormap, norm):
    rgb = colormap(norm(value))[:3]
    channels = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    luminance = .2126 * channels[0] + .7152 * channels[1] + .0722 * channels[2]
    light, dark = 1.05 / (luminance + .05), (luminance + .05) / .05
    return ("white", light) if light > dark else ("black", dark)


def _figure2(grid, seasons):
    matrix = np.asarray(grid["relative_percent"], dtype=float)
    bound = grid["color_bound"]
    colormap, norm = mpl.colormaps["RdBu_r"], TwoSlopeNorm(vmin=-bound, vcenter=0, vmax=bound)
    top, plot_end = 6, 6 + HEADER + 15 * PITCH
    canvas = _Canvas(plot_end + 58)
    block_width = (canvas.width - 18) / 2
    mapping = []
    for crop, left in (("rice", 0), ("maize", block_width + 18)):
        indexes = [i for i, key in enumerate(grid["row_keys"]) if key[0] == crop]
        grid_left, grid_top = left + 89, top + HEADER
        grid_width, grid_height = block_width - 89 - 6, len(indexes) * PITCH
        cell_width = grid_width / 4
        ax = canvas.axes(grid_left, grid_top, grid_width, grid_height)
        ax.imshow(matrix[indexes], cmap=colormap, norm=norm, interpolation="nearest", aspect="auto")
        ax.axvline(1.5, color="#858d93", linewidth=2)
        canvas.text(left + 7, top + 7.5, ("(A) " if crop == "rice" else "(B) ") + crop.title(), ha="left", weight="bold")
        for group, label in enumerate(("LOSO", "LOYO")):
            canvas.text(grid_left + (2 * group + 1) * cell_width, top + 7.5, label, weight="bold")
        for column, label in enumerate(("Ridge", "RF", "Ridge", "RF")):
            x = grid_left + column * cell_width
            canvas.text(x + cell_width / 2, top + 25, label,
                        region=(x + 1, top + 16, x + cell_width - 1, grid_top - 1))
        for i, index in enumerate(indexes):
            _, site, year = grid["row_keys"][index]
            y = grid_top + i * PITCH
            canvas.text(grid_left - 5, y + PITCH / 2, f"{site} {year}", ha="right",
                        region=(left + 3, y, grid_left - 2, y + PITCH))
            for j, value in enumerate(matrix[index]):
                x = grid_left + j * cell_width
                ink, ratio = _cell_ink(value, colormap, norm)
                label = f"{value:+.1f}".replace("-", "−")
                canvas.text(x + cell_width / 2, y + PITCH / 2, label, color=ink,
                            region=(x + 1, y, x + cell_width - 1, y + PITCH))
                axis, family = grid["column_keys"][j]
                record = seasons[(crop, site, year, axis, family)]
                mapping.append({"crop": crop, "site_id": site, "year": year, "axis": axis, "family": family,
                                "n": record["n"], "rmse_arm": record["rmse_arm"], "rmse_reference": record["rmse_ref"],
                                "relative_percent": float(value), "display_label": label, "text_color": ink,
                                "text_contrast_ratio": ratio, "x_pt": x + cell_width / 2, "y_pt": y + PITCH / 2,
                                "sample_x_pt": x + .12 * cell_width, "sample_y_pt": y + .12 * PITCH,
                                "background_rgb": np.round(np.array(colormap(norm(value))[:3]) * 255).astype(int).tolist()})
    bar_width = 165
    left, top = (canvas.width - bar_width) / 2, plot_end + 12
    colorbar = canvas.axes(left, top, bar_width, 7.5)
    colorbar.imshow(np.linspace(-bound, bound, 256)[None, :], extent=(-bound, bound, 0, 1), norm=norm,
                    cmap=colormap, interpolation="nearest", aspect="auto")
    colorbar.vlines((-12, -6, 0, 6, 12), 0, .38, colors="#485159", linewidth=2, clip_on=False)
    for value in (-12, -6, 0, 6, 12):
        canvas.text(left + (value + bound) / (2 * bound) * bar_width, top + 18,
                    f"{value:+d}".replace("-", "−") if value else "0")
    canvas.text(canvas.width / 2, top + 38, "C vs S RMSE change (%)")
    return canvas, mapping


def _save(canvas, number, mapping, output_dir):
    check = canvas.audit()
    stem = f"Figure_{number}"
    svg_path = output_dir / f"{stem}.svg"
    canvas.figure.savefig(svg_path, format="svg", metadata={"Date": None, "Title": f"Figure {number} at 180 mm"})
    svg = svg_path.read_text(encoding="utf-8")
    svg_root = ET.fromstring(svg)
    strokes = [float(w) for w in re.findall(r"stroke-width:\s*([\d.]+)", svg)]
    _require(bool(strokes) and min(strokes) >= 2, f"Figure {number}: visible strokes below 2 pt")
    labels = re.findall(r"<!--\s(.*?)\s-->", svg)
    if number == 1:
        _require(labels.count("(A)") == labels.count("(B)") == 1, "Figure 1 panel labels changed")
        markers = [el for el in svg_root.iter("{http://www.w3.org/2000/svg}use")
                   if any(f"fill: {color}" in el.attrib.get("style", "") for color, _, _ in CONTRASTS.values())]
        _require(len(markers) == 18, "Figure 1 requires 16 data marks and two legend marks")
        for marker, record in zip(markers[:16], mapping):
            _require(math.isclose(float(marker.attrib["x"]), record["x_pt"], abs_tol=1e-5) and
                     math.isclose(float(marker.attrib["y"]), record["y_pt"], abs_tol=1e-5) and
                     record["color"] in marker.attrib["style"], "Figure 1 SVG mark position/color changed")
        check["checked_points"] = 16
    else:
        _require(labels.count("(A) Rice") == labels.count("(B) Maize") == 1, "Figure 2 panel labels changed")
        value_labels = [label for label in labels if re.fullmatch(r"[+−]\d+\.\d", label)]
        _require(value_labels == [r["display_label"] for r in mapping], "Figure 2 SVG displayed values/order changed")
        check.update({"checked_cells": 116, "signed_zero_labels": sum(r["display_label"] in ("+0.0", "−0.0") for r in mapping),
                      "min_text_contrast_ratio": min(r["text_contrast_ratio"] for r in mapping)})
    raster_width = round(WIDTH_MM / 25.4 * DPI)
    canvas.figure.set_size_inches(raster_width / DPI, canvas.height / 72)
    png_path, tiff_path = output_dir / f"{stem}.png", output_dir / f"{stem}.tiff"
    canvas.figure.savefig(png_path, format="png", dpi=DPI, facecolor="white")
    with Image.open(png_path) as image:
        image.convert("RGB").save(tiff_path, format="TIFF", dpi=(DPI, DPI), compression="tiff_lzw")
    with Image.open(tiff_path) as image:
        _require(image.mode == "RGB" and image.info["dpi"] == (float(DPI), float(DPI)), "TIFF mode/DPI mismatch")
        _require(image.width == 4252 and abs(image.width / DPI * 25.4 - WIDTH_MM) < .005, "TIFF width mismatch")
        if number == 2:
            pixels = np.asarray(image)
            for record in mapping:
                x = int(record["sample_x_pt"] * image.width / canvas.width)
                y = int(record["sample_y_pt"] * image.height / canvas.height)
                _require(int(np.max(np.abs(pixels[y, x].astype(int) - record["background_rgb"]))) <= 1,
                         "Figure 2 raster cell color mismatch")
            check["verified_tiff_cell_rgb"] = 116
        check.update({"dimensions_px": list(image.size), "dpi": [float(v) for v in image.info["dpi"]], "mode": image.mode,
                      "width_mm": image.width / DPI * 25.4, "visible_stroke_min_pt": min(strokes),
                      "tiff_compression": image.info.get("compression")})
    check["outputs"] = {p.name: _sha(p) for p in (svg_path, png_path, tiff_path)}
    check["source_mapping"] = mapping
    canvas.figure.clear()
    return check


def render_figures(data_dir: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """Create final-layout Figure 1/2 SVG, 600 dpi PNG/TIFF, and captions.

    ``data_dir`` must contain FIGURE_SOURCE.json, SCORES.json, and
    ALL_CONTRASTS.json.  Only these aggregate JSONs are read.  Existing files
    with the named figure outputs in ``output_dir`` are replaced.  The return
    value is JSON-serializable and records source/value/layout checks; it does
    not claim that historical model fits have been independently rerun.

    Arial is the submission reference font.  On systems without Arial,
    Matplotlib may select a fallback; numeric checks remain meaningful, but
    identical raster bytes/layout require the recorded font and runtime.
    """
    data_dir, output_dir = Path(data_dir).resolve(), Path(output_dir).resolve()
    _require(data_dir != output_dir, "Use a separate output directory")
    figure, points, source_hashes, _, seasons = _load_aggregates(data_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    font_path = Path(findfont(FontProperties(family=["Arial"]), fallback_to_default=True))
    report = {"status": "AGGREGATE_FIGURE_REGENERATION_PASS", "scope": "aggregate-to-figure rendering only",
              "source_hashes": source_hashes, "matplotlib": mpl.__version__, "numpy": np.__version__,
              "font_requested": "Arial", "font_resolved_file": font_path.name, "font_sha256": _sha(font_path),
              "new_fits": 0, "new_predictions": 0, "model_replays": 0, "figures": {}}
    with mpl.rc_context({"font.family": "Arial", "font.size": FONT_PT, "svg.fonttype": "path",
                         "svg.hashsalt": "gpp-publication-widths"}):
        for number in (1, 2):
            canvas, mapping = _figure1(points) if number == 1 else _figure2(figure["figure2"], seasons)
            report["figures"][f"Figure_{number}"] = _save(canvas, number, mapping, output_dir)
    captions = output_dir / "FIGURE_CAPTIONS_EN.txt"
    captions.write_text(FINAL_CAPTIONS, encoding="utf-8")
    report["captions_sha256"] = _sha(captions)
    _require(all(_sha(data_dir / name) == sha for name, sha in source_hashes.items()), "Aggregate inputs changed during rendering")
    report["source_hashes_unchanged"] = True
    return report

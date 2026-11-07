"""Command line entry points for aggregate verification and regeneration."""

import argparse
import json
from pathlib import Path
import platform

from .validation import verify_inputs


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify or regenerate H2 results from aggregate JSON files.")
    parser.add_argument("command", choices=("verify", "tables", "figures", "reproduce"))
    parser.add_argument("--data-dir", type=Path, required=True, help="Public aggregate input directory")
    parser.add_argument("--output-dir", type=Path, help="New output directory for regeneration")
    parser.add_argument("--receipt", type=Path, help="Optional independent aggregate-verification receipt")
    args = parser.parse_args(argv)
    if args.command != "verify" and args.output_dir is None:
        parser.error("--output-dir is required for regeneration")
    try:
        if args.receipt and args.receipt.exists():
            raise ValueError("Receipt already exists: " + str(args.receipt))
        if args.receipt and args.output_dir and args.receipt.resolve().is_relative_to(args.output_dir.resolve()):
            raise ValueError("Use an independent receipt path outside the regeneration output directory")
        verification = verify_inputs(args.data_dir)
        result = {"command": args.command, "verification": verification,
                  "python": platform.python_version(), "version": "1.0.0"}
        if args.command != "verify":
            if args.command in ("tables", "reproduce"):
                from .tables import render_tables
            if args.command in ("figures", "reproduce"):
                from .figures import render_figures
            output_dir = args.output_dir.resolve()
            # Reserve the destination before writing any outputs; failed runs cannot overwrite prior releases.
            output_dir.mkdir(parents=True, exist_ok=False)
            if args.command in ("tables", "reproduce"):
                paths = render_tables(args.data_dir, output_dir / "tables")
                result["tables"] = [str(Path(path).relative_to(output_dir)) for path in paths]
            if args.command in ("figures", "reproduce"):
                result["figures"] = render_figures(args.data_dir, output_dir / "figures")
            write_json(output_dir / "AGGREGATE_REGENERATION_RECEIPT.json", result)
        if args.receipt:
            write_json(args.receipt, result)
        print(json.dumps({"status": "PASS", "command": args.command,
                          "metric_rows": verification["metric_rows"],
                          "paired_contrasts": verification["paired_contrasts"],
                          "new_fits": 0, "new_predictions": 0, "model_replays": 0}, indent=2))
        return 0
    except (OSError, ValueError, KeyError, ImportError) as error:
        parser.exit(1, f"h2-gpp: {error}\n")

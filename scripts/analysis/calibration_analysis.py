#!/usr/bin/env python3
"""Calibration diagnostics for the frozen C1 predictive stores.

The analysis is descriptive and does not alter any preregistered decision.
It uses the persisted posterior samples and targets, reports coverage and PIT
diagnostics per coordinate, and clusters uncertainty intervals by asset.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


COORDINATES = ("h1", "h2", "delta_T")
LEVELS = (0.50, 0.80, 0.90)
MODELS = ("prop-direct", "b-stdprob")
SPLITS = ("test", "lockbox")


def load_store(path: Path) -> dict[str, np.ndarray | dict]:
    with np.load(path, allow_pickle=False) as archive:
        metadata = json.loads(str(archive["metadata_json"].item()))
        return {
            "metadata": metadata,
            "samples": np.asarray(archive["samples_metric"], dtype=np.float64),
            "targets": np.asarray(archive["target_metric"], dtype=np.float64),
            "assets": np.asarray(archive["asset_ids"]).astype(str),
        }


def row_diagnostics(samples: np.ndarray, targets: np.ndarray) -> dict[str, np.ndarray]:
    """Return per-row interval coverage and randomized PIT values."""

    flat = samples.reshape(samples.shape[0], -1, samples.shape[-1])
    coverage = np.empty((flat.shape[0], len(LEVELS), flat.shape[-1]), dtype=float)
    for level_index, level in enumerate(LEVELS):
        lower, upper = np.quantile(flat, [(1 - level) / 2, 1 - (1 - level) / 2], axis=1)
        coverage[:, level_index, :] = ((targets >= lower) & (targets <= upper)).astype(float)

    less = (flat < targets[:, None, :]).sum(axis=1)
    equal = (flat == targets[:, None, :]).sum(axis=1)
    # Mid-rank PIT is deterministic and handles the rare exact tie.
    pit = (less + 0.5 * equal) / flat.shape[1]
    return {"coverage": coverage, "pit": pit}


def asset_means(values: np.ndarray, assets: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    unique = np.unique(assets)
    means = np.asarray([values[assets == asset].mean(axis=0) for asset in unique])
    return unique, means


def bootstrap_asset_mean(values: np.ndarray, assets: np.ndarray, *, seed: int, reps: int = 2000) -> dict:
    _, means = asset_means(values, assets)
    rng = np.random.default_rng(seed)
    draw = rng.integers(0, len(means), size=(reps, len(means)))
    estimates = means[draw].mean(axis=1)
    return {
        "estimate": float(means.mean()),
        "ci_lower": float(np.quantile(estimates, 0.05)),
        "ci_upper": float(np.quantile(estimates, 0.95)),
        "assets": int(len(means)),
        "replicates": int(reps),
        "seed": int(seed),
        "unit": "asset",
    }


def asset_histogram_l1(values: np.ndarray, assets: np.ndarray) -> dict:
    """Mean asset-level L1 distance between PIT-bin frequencies and Uniform(0,1)."""

    unique = np.unique(assets)
    rows = []
    for asset in unique:
        counts = np.histogram(values[assets == asset], bins=np.linspace(0, 1, 11))[0]
        frequencies = counts / counts.sum()
        rows.append(float(np.mean(np.abs(frequencies - 0.1))))
    return {"estimate": float(np.mean(rows)), "assets": int(len(rows)), "bins": 10}


def summarize(store: dict, *, split: str, model: str, seed_offset: int) -> dict:
    samples = store["samples"]
    targets = store["targets"]
    assets = store["assets"]
    diagnostics = row_diagnostics(samples, targets)
    coverage = diagnostics["coverage"]
    pit = diagnostics["pit"]
    row_summary = {}
    for level_index, level in enumerate(LEVELS):
        row_summary[str(level)] = {
            COORDINATES[d]: bootstrap_asset_mean(
                coverage[:, level_index, d], assets, seed=20261003 + seed_offset + level_index * 17 + d
            )
            for d in range(len(COORDINATES))
        }
    pit_summary = {}
    for d, coordinate in enumerate(COORDINATES):
        values = pit[:, d]
        pit_summary[coordinate] = {
            "mean": bootstrap_asset_mean(values, assets, seed=20261103 + seed_offset + d),
            "histogram_l1": asset_histogram_l1(values, assets),
            "histogram": np.histogram(values, bins=np.linspace(0, 1, 11))[0].astype(int).tolist(),
        }
    return {
        "split": split,
        "model": model,
        "metadata": store["metadata"],
        "rows": int(samples.shape[0]),
        "assets": int(np.unique(assets).size),
        "predictive_samples": int(samples.shape[1] * samples.shape[2]),
        "coordinates": list(COORDINATES),
        "central_coverage": row_summary,
        "pit": pit_summary,
    }


def make_figure(summaries: list[dict], output: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), constrained_layout=True)
    colors = {"PROP-DIRECT": "#1f77b4", "B-STDPROB": "#d62728"}
    markers = {"test": "o", "lockbox": "s"}
    nominal = np.asarray(LEVELS)
    for summary in summaries:
        values = [
            np.mean([summary["central_coverage"][str(level)][coordinate]["estimate"] for coordinate in COORDINATES])
            for level in LEVELS
        ]
        axes[0].plot(
            nominal,
            values,
            marker=markers[summary["split"]],
            color=colors[summary["model"]],
            linewidth=1.5,
            label=f"{summary['model']} ({summary['split']})",
        )
    axes[0].plot([0, 1], [0, 1], color="0.35", linestyle="--", linewidth=1)
    axes[0].set(xlabel="Nominal central coverage", ylabel="Empirical coverage", xlim=(0.45, 0.95), ylim=(0.45, 0.95))
    axes[0].grid(alpha=0.2)

    for summary in summaries:
        hist = np.mean([summary["pit"][coordinate]["histogram"] for coordinate in COORDINATES], axis=0)
        hist = hist / hist.sum()
        centers = np.linspace(0.05, 0.95, 10)
        axes[1].plot(
            centers,
            hist,
            marker=markers[summary["split"]],
            color=colors[summary["model"]],
            linewidth=1.5,
            label=f"{summary['model']} ({summary['split']})",
        )
    axes[1].axhline(0.1, color="0.35", linestyle="--", linewidth=1)
    axes[1].set(xlabel="PIT bin", ylabel="Frequency", xlim=(0, 1), ylim=(0, None))
    axes[1].grid(alpha=0.2)
    axes[1].legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
    fig.savefig(output, dpi=240, bbox_inches="tight")
    plt.close(fig)


def latex_table(summaries: list[dict], output: Path) -> None:
    lines = [
        r"\begin{table}[tb]",
        r"\centering",
        r"\caption{\textbf{Posterior calibration diagnostics on the C1 evaluation splits.} Coverage entries are averaged over the three joint coordinates and include 90\% asset-bootstrap intervals. PIT histogram L1 is a descriptive distance from a uniform histogram; zero is ideal.}",
        r"\label{tab:calibration}",
        r"\begin{tabular}{llcc}",
        r"\toprule",
        r"Model & Split & 90\% coverage & PIT histogram L1 \\",
        r"\midrule",
    ]
    for summary in summaries:
        coverage = [summary["central_coverage"]["0.9"][c] for c in COORDINATES]
        estimate = np.mean([x["estimate"] for x in coverage])
        low = np.mean([x["ci_lower"] for x in coverage])
        high = np.mean([x["ci_upper"] for x in coverage])
        pit = [summary["pit"][c]["histogram_l1"]["estimate"] for c in COORDINATES]
        pit_est = np.mean(pit)
        model = r"\propdirect{}" if summary["model"] == "PROP-DIRECT" else r"\bstdprob{}"
        lines.append(f"{model} & {summary['split']} & {estimate:.3f} [{low:.3f}, {high:.3f}] & {pit_est:.3f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("calibration_results"))
    parser.add_argument(
        "--manuscript-dir",
        type=Path,
        default=None,
        help="Optional manuscript directory for the figure and LaTeX table outputs.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    output = (root / args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    summaries = []
    for split_index, split in enumerate(SPLITS):
        for model_index, model in enumerate(MODELS):
            paths = sorted((root / "formal_runs/f2_c1_outcome_aware_0.1.0" / split / "sealed/predictions" / model).glob("seed-*.npz"))
            if not paths:
                raise FileNotFoundError(f"No prediction stores for {split}/{model}")
            per_seed = [summarize(load_store(path), split=split, model=model.upper(), seed_offset=split_index * 1000 + model_index * 100 + seed_index * 10) for seed_index, path in enumerate(paths)]
            # Keep seed-specific results and a simple macro summary for the paper-facing diagnostic.
            summaries.extend(per_seed)
    result = {
        "analysis": "descriptive posterior calibration",
        "coordinates": list(COORDINATES),
        "nominal_levels": list(LEVELS),
        "bootstrap": {"replicates": 2000, "confidence": 0.90, "unit": "asset"},
        "stores": summaries,
    }
    (output / "calibration_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    # Use seed-macro averages for the compact manuscript table and figure.
    compact = []
    for model in ("PROP-DIRECT", "B-STDPROB"):
        for split in SPLITS:
            group = [item for item in summaries if item["model"] == model and item["split"] == split]
            first = group[0]
            merged = json.loads(json.dumps(first))
            for level in merged["central_coverage"]:
                for coordinate in COORDINATES:
                    for key in ("estimate", "ci_lower", "ci_upper"):
                        merged["central_coverage"][level][coordinate][key] = float(np.mean([item["central_coverage"][level][coordinate][key] for item in group]))
            for coordinate in COORDINATES:
                key = "mean"
                for metric_key in ("estimate", "ci_lower", "ci_upper"):
                    merged["pit"][coordinate][key][metric_key] = float(np.mean([item["pit"][coordinate][key][metric_key] for item in group]))
                merged["pit"][coordinate]["histogram_l1"]["estimate"] = float(np.mean([item["pit"][coordinate]["histogram_l1"]["estimate"] for item in group]))
                merged["pit"][coordinate]["histogram"] = np.mean([item["pit"][coordinate]["histogram"] for item in group], axis=0).tolist()
            compact.append(merged)
    if args.manuscript_dir is not None:
        manuscript_dir = (root / args.manuscript_dir).resolve()
        (manuscript_dir / "figures").mkdir(parents=True, exist_ok=True)
        (manuscript_dir / "tables").mkdir(parents=True, exist_ok=True)
        figure_path = manuscript_dir / "figures/fig7_calibration_reliability.png"
        table_path = manuscript_dir / "tables/calibration_table.tex"
        make_figure(compact, figure_path)
        latex_table(compact, table_path)
        print(f"Wrote {figure_path}")
        print(f"Wrote {table_path}")
    (output / "calibration_compact.json").write_text(json.dumps(compact, indent=2), encoding="utf-8")
    print(f"Wrote {output / 'calibration_results.json'}")


if __name__ == "__main__":
    main()

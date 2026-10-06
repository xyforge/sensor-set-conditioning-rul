#!/usr/bin/env python3
"""Summarize the post-hoc oracle-relative geometry audit.

The frozen C2 audit already stores g_error = |d_model - d_oracle| for each
paired case and optimization seed.  This script averages seeds within each
case, averages query cases within asset and pair class, and applies the same
asset bootstrap convention used for the C2 descriptive summaries.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
_FULL_AUDIT_PATH = ROOT / "formal_runs/f3_c2_information_loss_a40_0.1.0/test/score/c2_pair_distance_audit.npz"
_PACKAGED_AUDIT_PATH = ROOT / "reproducibility/oracle_audit/c2_pair_distance_audit_test.npz"
AUDIT_PATH = _FULL_AUDIT_PATH if _FULL_AUDIT_PATH.exists() else _PACKAGED_AUDIT_PATH
OUTPUT_DIR = ROOT / "scripts/analysis/outputs"
TABLE_PATH = OUTPUT_DIR / "oracle_alignment_table.tex"
MODELS = ("PROP-DIRECT", "B-STDPROB")
SEEDS = (1701, 2303, 2909)
PAIR_CLASSES = ("critical_parent", "critical_matched_random", "critical_redundant")
BOOTSTRAP_REPLICATES = 2000
BOOTSTRAP_SEED = 2026091803


def _asset_values(values: np.ndarray, assets: np.ndarray, pair_classes: np.ndarray, pair_class: str) -> np.ndarray:
    unique_assets = np.unique(assets)
    return np.asarray(
        [values[(assets == asset) & (pair_classes == pair_class)].mean() for asset in unique_assets],
        dtype=np.float64,
    )


def _latex_signed_sci(value: float) -> str:
    """Format a signed value in compact LaTeX scientific notation."""
    sign = "+" if value >= 0 else "-"
    mantissa, exponent = f"{abs(value):.1e}".split("e")
    return f"{sign}{mantissa}\\times10^{{{int(exponent)}}}"


def _bootstrap(values: np.ndarray, rng: np.random.Generator) -> dict[str, float | int]:
    draws = rng.integers(0, len(values), size=(BOOTSTRAP_REPLICATES, len(values)))
    estimates = values[draws].mean(axis=1)
    return {
        "estimate": float(values.mean()),
        "ci_lower": float(np.quantile(estimates, 0.05)),
        "ci_upper": float(np.quantile(estimates, 0.95)),
        "assets": int(len(values)),
        "replicates": BOOTSTRAP_REPLICATES,
        "seed": BOOTSTRAP_SEED,
    }


def main() -> None:
    if not AUDIT_PATH.exists():
        raise FileNotFoundError(AUDIT_PATH)
    with np.load(AUDIT_PATH, allow_pickle=False) as audit:
        pair_classes = audit["pair_class"].astype(str)
        assets = audit["asset_id"].astype(str)
        rng = np.random.default_rng(BOOTSTRAP_SEED)
        result: dict[str, object] = {
            "source": str(AUDIT_PATH.relative_to(ROOT)),
            "estimand": "oracle_relative_geometry_error = abs(model_energy_distance - oracle_energy_distance)",
            "aggregation": "mean across optimization seeds; query cases within asset and pair class; mean across assets",
            "bootstrap_unit": "asset",
            "pair_classes": {},
        }
        latex_rows: list[str] = []
        for pair_class in PAIR_CLASSES:
            model_asset_values = {
                model: _asset_values(
                    np.mean(
                        [audit[f"g_error|{model}|seed{seed}"] for seed in SEEDS],
                        axis=0,
                    ),
                    assets,
                    pair_classes,
                    pair_class,
                )
                for model in MODELS
            }
            delta = model_asset_values["PROP-DIRECT"] - model_asset_values["B-STDPROB"]
            block = {
                "PROP-DIRECT": _bootstrap(model_asset_values["PROP-DIRECT"], rng),
                "B-STDPROB": _bootstrap(model_asset_values["B-STDPROB"], rng),
                "PROP-DIRECT_minus_B-STDPROB": _bootstrap(delta, rng),
            }
            result["pair_classes"][pair_class] = block
            prop = block["PROP-DIRECT"]["estimate"]
            base = block["B-STDPROB"]["estimate"]
            d = block["PROP-DIRECT_minus_B-STDPROB"]
            label = {
                "critical_parent": "Critical vs. full",
                "critical_matched_random": "Critical vs. matched random",
                "critical_redundant": "Critical vs. redundant",
            }[pair_class]
            latex_rows.append(
                f"{label} & {prop:.4f} & {base:.4f} & "
                f"${_latex_signed_sci(d['estimate'])}$ "
                f"$[{_latex_signed_sci(d['ci_lower'])}, {_latex_signed_sci(d['ci_upper'])}]$ \\\\"
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = OUTPUT_DIR / "oracle_alignment_summary.json"
    summary_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    TABLE_PATH.write_text(
        r'''\begin{table}[tb]
  \centering
  \caption{\textbf{Exploratory oracle-relative geometry error on the C2 evaluation.}
  Values are asset-level means of $E_{\mathrm{geometry}}=|d_{\mathrm{model}}-d_{\mathrm{oracle}}|$;
  lower values indicate closer agreement with the oracle geometry. The final column
  reports the paired PROP-DIRECT minus B-STDPROB difference with a 90\% asset-bootstrap
  interval (2,000 replicates). This analysis is secondary and was not used in any
  preregistered decision rule.}
  \label{tab:oracle_alignment}
  \resizebox{\linewidth}{!}{%
  \begin{tabular}{lccc}
    \toprule
    Pair class & PROP-DIRECT & B-STDPROB & Difference [90\% CI] \\
    \midrule
'''
        + "\n".join("    " + row for row in latex_rows)
        + r'''
    \bottomrule
  \end{tabular}%
  }
\end{table}
''',
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    print(f"Wrote {summary_path}")
    print(f"Wrote {TABLE_PATH}")


if __name__ == "__main__":
    main()

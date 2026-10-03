# C-MAPSS shared-model rerun report

Run date: 2026-10-03. The run was executed on a dual NVIDIA A40 host using Python 3.11 with PyTorch 2.3.1+cu121, NumPy 1.26.4, and SciPy 1.17.1.

## Protocol

- One PROP-DIRECT and one B-STDPROB model were trained across `full`, `view_1`, and `view_2`.
- Training used 80 engines and engine-level validation used 20 engines; the three views were merged only after the engine split.
- The shared training set contained 4,380 masked windows and validation contained 1,071 masked windows.
- The official 100 FD001 test engines were evaluated with 128 MC-dropout samples per view.
- Geometry confidence intervals use 2,000 engine bootstrap replicates at 90% confidence.
- Training seed: 42. Evaluation/bootstrap/dropout seed: 42 for posterior generation and 20261003 for relative-reduction bootstrap.

## Results

| Pair | PROP-DIRECT energy distance | B-STDPROB energy distance | Relative reduction (90% CI) |
|---|---:|---:|---:|
| Full vs View 1 | 1.85 [1.61, 2.11] | 2.27 [2.04, 2.51] | 18.5% [7.8%, 29.3%] |
| Full vs View 2 | 1.80 [1.56, 2.05] | 2.54 [2.29, 2.79] | 28.9% [18.4%, 37.9%] |
| View 1 vs View 2 | 1.85 [1.57, 2.17] | 1.36 [1.19, 1.52] | -36.6% [-62.9%, -13.1%] |

Single-view test MAE (full / View 1 / View 2) was 16.44 / 15.95 / 16.25 cycles for PROP-DIRECT and 16.27 / 15.42 / 15.73 cycles for B-STDPROB.

## Interpretation before manuscript integration

The shared protocol preserves a geometry advantage for comparisons with the full view, but the matched-cardinality reduced-view comparison reverses the ordering. This is evidence for a view-specific boundary, not a uniform external confirmation of PROP-DIRECT. The C-MAPSS section should be rewritten around this interaction and should retain the simulated-benchmark scope.

The evaluator initially lacked a fixed posterior-sampling seed; that was corrected before the final result. A repeat evaluation with the same checkpoint and seed produced an identical JSON result.

Raw artifacts are in `shared_seed42_remote/`; model checkpoints and training summaries are in `../cmapss_models_shared/`.

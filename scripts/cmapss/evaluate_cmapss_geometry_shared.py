#!/usr/bin/env python3
"""
评估 shared-model 的跨视图几何一致性（审稿人 P0-1 重跑对应评估）
====================================================================

与 evaluate_cmapss_geometry.py 的区别：
- specialist 版：每个视图用各自 checkpoint 生成后验 → 跨视图距离
  （该协议违背论文方法定义，见 train_cmapss_shared.py 文件头）
- 本脚本：单一 shared-model 在所有视图下生成后验 → 跨视图距离
  （与合成数据实验协议一致）

输出：
- cmapss_results/cmapss_shared_geometry_results.json
- 论文表格用 LaTeX 片段（含 bootstrap 90% CI，按 engine 重采样）

运行（在 train_cmapss_shared.py 完成后）：
    python scripts/cmapss/evaluate_cmapss_geometry_shared.py
"""

import torch
import numpy as np
import pickle
import os
import json
from pathlib import Path
from typing import Dict, List
from scipy.stats import energy_distance

# 复用 specialist 评估脚本的采样与距离函数
from evaluate_cmapss_geometry import generate_posterior_samples
from train_cmapss import PROP_DIRECT_CMAPSS, B_STDPROB_CMAPSS


def load_shared_model(checkpoint_path: str, model_name: str, n_sensors: int,
                      device: str):
    if model_name == 'PROP-DIRECT':
        model = PROP_DIRECT_CMAPSS(n_sensors=n_sensors, hidden_dim=128,
                                   num_layers=2, sensor_embed_dim=32)
    elif model_name == 'B-STDPROB':
        model = B_STDPROB_CMAPSS(n_sensors=n_sensors, hidden_dim=128, num_layers=2)
    else:
        raise ValueError(f"Unknown model: {model_name}")

    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    return model


def evaluate_shared_cross_view(
    model_name: str,
    views_data: Dict,
    view_names: List[str],
    model_dir: str,
    n_sensors: int,
    n_posterior_samples: int = 128,
    device: str = 'cuda:0',
    n_bootstrap: int = 2000,
    confidence: float = 0.9,
    seed: int = 42
) -> Dict:
    """
    用单一 shared-model 在所有视图下评估跨视图一致性。

    注意与 specialist 评估的关键差异：
    - 同一模型、同一组参数，只是输入视图（mask + 传感器子集）不同
    - 这正是论文方法定义的"观测过程条件化"所要满足的评估
    """
    model_dir = Path(model_dir)
    # Fix the dropout stream so repeated evaluations of the same checkpoint
    # produce the same posterior samples and geometry estimates.
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    checkpoint_path = model_dir / f"{model_name}_shared_best.pt"
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Shared model not found: {checkpoint_path}\n"
            f"请先运行 train_cmapss_shared.py"
        )

    model = load_shared_model(str(checkpoint_path), model_name, n_sensors, device)
    training_result_path = model_dir / f"{model_name}_shared_results.json"
    training_result = {}
    if training_result_path.exists():
        with open(training_result_path) as f:
            training_result = json.load(f)
    print(f"\n{'='*60}")
    print(f"  Evaluating SHARED {model_name} cross-view consistency")
    print(f"  (single model, {len(view_names)} views)")
    print(f"{'='*60}")

    # 1. 同一模型在所有视图下生成后验样本
    posterior_samples = {}
    for view_name in view_names:
        view_data = views_data['views'][view_name]
        test_windows = torch.FloatTensor(view_data['test_windows']).to(device)
        test_units = np.asarray(view_data['test_units'])
        if view_name != view_names[0] and not np.array_equal(
            test_units, posterior_samples[view_names[0]]['units']
        ):
            raise ValueError(f"Test engine ordering differs between {view_names[0]} and {view_name}")

        sensor_mask_indices = view_data['mask']
        B, T, F = test_windows.shape
        sensor_mask = torch.zeros(B, F).to(device)
        sensor_mask[:, sensor_mask_indices] = 1.0

        samples = generate_posterior_samples(
            model, test_windows, sensor_mask,
            n_samples=n_posterior_samples, device=device
        )
        posterior_samples[view_name] = {
            'samples': samples, 'units': test_units
        }
        print(f"   {view_name}: {samples.shape}")

    # 2. Pairwise 能量距离
    n_units = len(posterior_samples[view_names[0]]['units'])
    view_pairs = [(view_names[i], view_names[j])
                  for i in range(len(view_names))
                  for j in range(i + 1, len(view_names))]

    pair_distances = {}
    for view_a, view_b in view_pairs:
        samples_a = posterior_samples[view_a]['samples']
        samples_b = posterior_samples[view_b]['samples']
        unit_distances = np.array([
            energy_distance(samples_a[u], samples_b[u])
            for u in range(n_units)
        ])
        pair_distances[f"{view_a}_vs_{view_b}"] = {
            'unit_distances': unit_distances,
            'mean': float(unit_distances.mean()),
            'std': float(unit_distances.std()),
        }
        print(f"   {view_a}_vs_{view_b}: {unit_distances.mean():.6f}")

    # 3. Bootstrap CI（按 engine unit 重采样）
    rng = np.random.RandomState(seed)
    alpha = (1 - confidence) / 2
    for pair_name, v in pair_distances.items():
        reps = []
        for _ in range(n_bootstrap):
            idx = rng.randint(0, n_units, size=n_units)
            reps.append(v['unit_distances'][idx].mean())
        reps = np.array(reps)
        v['bootstrap'] = {
            'mean': float(reps.mean()),
            'ci_lower': float(np.quantile(reps, alpha)),
            'ci_upper': float(np.quantile(reps, 1 - alpha)),
        }
        print(f"   {pair_name} CI: [{v['bootstrap']['ci_lower']:.6f}, "
              f"{v['bootstrap']['ci_upper']:.6f}]")

    return {
        'model_name': model_name,
        'regime': 'shared',
        'n_units': n_units,
        'n_posterior_samples': n_posterior_samples,
        'evaluation_config': {
            'n_sensors': n_sensors,
            'n_bootstrap': n_bootstrap,
            'confidence': confidence,
            'bootstrap_unit': 'engine',
            'seed': seed,
            'device': device,
            'view_names': view_names,
            'checkpoint': str(checkpoint_path),
        },
        'training_config': training_result.get('config', {}),
        'per_view_test_metrics': training_result.get('per_view_test_metrics', {}),
        'pair_distances': {
            k: {
                'mean': v['mean'],
                'std': v['std'],
                'unit_distances': v['unit_distances'].tolist(),
                'bootstrap': v['bootstrap'],
            }
            for k, v in pair_distances.items()
        }
    }


def compare_and_report(prop_results: Dict, bstd_results: Dict,
                       output_path: str):
    """对比两模型并生成论文用 LaTeX 表格片段。"""
    pairs = list(prop_results['pair_distances'].keys())
    improvements = {}
    for pair in pairs:
        p = prop_results['pair_distances'][pair]['mean']
        b = bstd_results['pair_distances'][pair]['mean']
        prop_units = np.asarray(prop_results['pair_distances'][pair]['unit_distances'])
        base_units = np.asarray(bstd_results['pair_distances'][pair]['unit_distances'])
        if prop_units.shape != base_units.shape:
            raise ValueError(f"Engine-level distance shape mismatch for {pair}")
        rng = np.random.RandomState(20261003)
        draws = rng.randint(0, len(prop_units), size=(2000, len(prop_units)))
        relative_draws = 1.0 - prop_units[draws].mean(axis=1) / base_units[draws].mean(axis=1)
        improvements[pair] = {
            'prop_mean': p,
            'baseline_mean': b,
            'relative_reduction_percent': float((b - p) / b * 100),
            'bootstrap': {
                'ci_lower': float(np.quantile(relative_draws, 0.05) * 100),
                'ci_upper': float(np.quantile(relative_draws, 0.95) * 100),
                'replicates': 2000,
                'seed': 20261003,
                'unit': 'engine',
            },
        }

    report = {
        'prop_results': prop_results,
        'bstd_results': bstd_results,
        'improvements': improvements,
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w') as f:
        json.dump(report, f, indent=2)

    # LaTeX 片段
    print("\n% LaTeX 表格片段（替换 tables/cmapss_validation.tex 中对应数值）")
    print("\\begin{tabular}{lccc}")
    print("\\toprule")
    print("\\textbf{View Pair} & \\textbf{PROP-DIRECT} & \\textbf{B-STDPROB} "
          "& \\textbf{Relative Reduction} \\\\")
    print("\\midrule")
    for pair in pairs:
        p = prop_results['pair_distances'][pair]
        b = bstd_results['pair_distances'][pair]
        imp = improvements[pair]['relative_reduction_percent']
        imp_boot = improvements[pair]['bootstrap']
        label = pair.replace('_', ' ').title()
        line = (
            f"{label} & {p['mean']:.2f} [{p['bootstrap']['ci_lower']:.2f}, "
            f"{p['bootstrap']['ci_upper']:.2f}] & {b['mean']:.2f} "
            f"[{b['bootstrap']['ci_lower']:.2f}, {b['bootstrap']['ci_upper']:.2f}] "
            f"& {imp:.1f}\\% [{imp_boot['ci_lower']:.1f}, "
            f"{imp_boot['ci_upper']:.1f}] " + r"\\"
        )
        print(line)
    print("\\bottomrule")
    print("\\end{tabular}")

    print(f"\n✅ Report saved to: {out}")


if __name__ == "__main__":
    device = os.getenv('CMAPSS_DEVICE') or ('cuda:0' if torch.cuda.is_available() else 'cpu')
    views_file = os.getenv('CMAPSS_VIEWS_FILE',
                           './cmapss_views/cmapss_views_random_seed42.pkl')
    model_dir = os.getenv('CMAPSS_SHARED_OUTPUT_DIR', './cmapss_models_shared')
    n_samples = int(os.getenv('CMAPSS_N_SAMPLES', '128'))

    with open(views_file, 'rb') as f:
        views_data = pickle.load(f)

    n_sensors = len(views_data['active_sensors'])
    view_names = ['full', 'view_1', 'view_2']

    results = {}
    for model_name in ['PROP-DIRECT', 'B-STDPROB']:
        results[model_name] = evaluate_shared_cross_view(
            model_name=model_name,
            views_data=views_data,
            view_names=view_names,
            model_dir=model_dir,
            n_sensors=n_sensors,
            n_posterior_samples=n_samples,
            device=device,
        )

    compare_and_report(
        results['PROP-DIRECT'],
        results['B-STDPROB'],
        output_path='./cmapss_results/cmapss_shared_geometry_results.json',
    )

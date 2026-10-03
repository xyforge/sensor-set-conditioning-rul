#!/usr/bin/env python3
"""
训练 C-MAPSS shared-model（跨观测配置的单一模型）
================================================================

【为什么需要这个脚本 —— 审稿人 P0-1】
原 train_cmapss.py 对每个视图独立训练一个模型（specialist regime），
与论文方法本身矛盾：
1. 论文方法的定义性设计是"单一模型跨观测配置共享参数"，
   sensor-set embedding 在训练中是变量，驱动跨视图后验几何学习；
2. specialist regime 下 sensor-set embedding 是常数，条件化机制从未被训练；
3. 论文引言明确批评 ensemble（每配置一模型）策略，specialist regime
   恰好就是 ensemble 的变体，与正文自相矛盾。

本脚本实现 shared-model 协议（与合成数据实验一致）：
- 训练集 = 所有视图的并集（同一窗口在多个视图下出现，
  sensor_mask 标识其来源视图）
- 单一 PROP-DIRECT / B-STDPROB 在混合配置上训练
- 评估：同一模型在不同视图下的跨视图后验一致性（energy distance）
  + 单视图 MAE（质量控制，防止 over-invariance 混淆）
- 报告 oracle-relative 检查所需的单视图质量与跨视图几何量

【运行方式（A40 服务器）】
    python scripts/cmapss/train_cmapss_shared.py
    或用环境变量：
    CMAPSS_MODEL_NAME=PROP-DIRECT CMAPSS_SEED=42 \\
        python scripts/cmapss/train_cmapss_shared.py

【输出】
- checkpoint: cmapss_models_shared/{model}_shared_best.pt
- 结果 JSON: cmapss_results/cmapss_shared_geometry_results.json
  （含跨视图能量距离、bootstrap CI、单视图 MAE、用于论文 Table 的 LaTeX）

注意：与 specialist 版本使用同一视图文件（cmapss_views_random_seed42.pkl），
保证两协议唯一的实验变量是"训练是否共享配置"。
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pickle
import os
import json
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm

# 复用 specialist 版本的模型定义，确保架构完全一致
from train_cmapss import (
    PROP_DIRECT_CMAPSS,
    B_STDPROB_CMAPSS,
    train_one_epoch,
    evaluate,
)


class SharedViewDataset(Dataset):
    """
    Shared-model 训练数据集：合并所有视图的窗口。

    与 CMAPSSDataset 的区别：
    - 每条样本携带自己的 sensor_mask（标识其视图），而不是全局单一 mask
    - 实现"训练数据包含多种观测过程"（论文 03_methods §Training Objective）
    """

    def __init__(self, windows_list, rul_list, mask_list):
        """
        Args:
            windows_list: List[np.ndarray], 每个元素 (N_v, T, F)，第 v 个视图的窗口
            rul_list: List[np.ndarray], 每个元素 (N_v,)
            mask_list: List[List[int]], 每个元素是该视图保留的传感器索引（视图级）
        """
        if not (len(windows_list) == len(rul_list) == len(mask_list)):
            raise ValueError("windows/rul/mask lists must have equal length")

        self.windows = torch.FloatTensor(np.concatenate(windows_list, axis=0))
        self.rul = torch.FloatTensor(np.concatenate(rul_list, axis=0))

        N_total, T, F = self.windows.shape
        masks = []
        for windows, keep_idx in zip(windows_list, mask_list):
            m = torch.zeros(len(windows), F)
            m[:, keep_idx] = 1.0
            masks.append(m)
        self.sensor_mask = torch.cat(masks, dim=0)

        if len(self.sensor_mask) != N_total:
            raise ValueError("Mask broadcast mismatch")

    def __len__(self):
        return len(self.windows)

    def __getitem__(self, idx):
        return {
            'windows': self.windows[idx],
            'sensor_mask': self.sensor_mask[idx],
            'rul': self.rul[idx]
        }


def build_shared_datasets(views_data: Dict, view_names: List[str], n_sensors: int,
                          val_fraction: float = 0.2, seed: int = 42):
    """
    构建 shared-model 的训练/验证/测试集。

    关键设计：按 engine unit 划分验证集（与 specialist 版本相同的划分规则），
    同一 unit 的所有视图样本整体划入训练或验证，避免跨视图泄漏。
    """
    # 按 unit 收集所有视图的窗口（每个视图下同一 unit 的窗口是同一退化轨迹的不同观测）
    rng = np.random.RandomState(seed)

    # 收集全部 unit（以 full 视图为准）
    full_view = views_data['views']['full']
    unique_units = np.unique(full_view['train_units'])
    rng.shuffle(unique_units)
    n_val = max(1, int(round(len(unique_units) * val_fraction)))
    val_units = set(unique_units[:n_val].tolist())
    fit_units = set(unique_units[n_val:].tolist())

    fit_windows, fit_rul, fit_masks = [], [], []
    val_windows, val_rul, val_masks = [], [], []
    test_windows, test_rul, test_masks = [], [], []

    for view_name in view_names:
        vd = views_data['views'][view_name]
        mask = vd['mask']
        tw = np.asarray(vd['train_windows'])
        tr = np.asarray(vd['train_rul'])
        tu = np.asarray(vd['train_units'])
        if tw.shape[-1] != n_sensors:
            raise ValueError(f"Feature dim mismatch in {view_name}")

        fit_idx = np.array([u in fit_units for u in tu], dtype=bool)
        val_idx = ~fit_idx

        fit_windows.append(tw[fit_idx]); fit_rul.append(tr[fit_idx])
        fit_masks.append(mask)

        val_windows.append(tw[val_idx]); val_rul.append(tr[val_idx])
        val_masks.append(mask)

        test_windows.append(np.asarray(vd['test_windows']))
        test_rul.append(np.asarray(vd['test_rul']))
        test_masks.append(mask)

    train_dataset = SharedViewDataset(fit_windows, fit_rul, fit_masks)
    val_dataset = SharedViewDataset(val_windows, val_rul, val_masks)

    # 测试集按视图分开保留（用于逐视图评估与跨视图配对）
    test_by_view = {
        name: SharedViewDataset([w], [r], [m])
        for name, w, r, m in zip(view_names, test_windows, test_rul, test_masks)
    }

    return train_dataset, val_dataset, test_by_view, len(fit_units), len(val_units)


def train_shared_model(
    model_name: str,
    views_data: Dict,
    view_names: List[str],
    n_sensors: int,
    device: str = 'cuda:0',
    batch_size: int = 256,
    epochs: int = 100,
    lr: float = 0.001,
    early_stop_patience: int = 15,
    output_dir: str = './cmapss_models_shared',
    val_fraction: float = 0.2,
    seed: int = 42
) -> Dict:
    """训练单个 shared-model（跨配置共享参数）。"""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    train_dataset, val_dataset, test_by_view, n_fit, n_val = build_shared_datasets(
        views_data, view_names, n_sensors, val_fraction, seed
    )

    print(f"\n{'='*60}")
    print(f"  Training SHARED {model_name} across {len(view_names)} views")
    print(f"  Views: {view_names}")
    print(f"  Train units (shared): {n_fit}  |  Val units: {n_val}")
    print(f"  Train windows: {len(train_dataset)}  |  Val windows: {len(val_dataset)}")
    print(f"{'='*60}")

    pin = str(device).startswith('cuda')
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True,
                              num_workers=0, pin_memory=pin)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False,
                            num_workers=0, pin_memory=pin)

    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    if model_name == 'PROP-DIRECT':
        model = PROP_DIRECT_CMAPSS(n_sensors=n_sensors, hidden_dim=128,
                                   num_layers=2, sensor_embed_dim=32)
    elif model_name == 'B-STDPROB':
        model = B_STDPROB_CMAPSS(n_sensors=n_sensors, hidden_dim=128, num_layers=2)
    else:
        raise ValueError(f"Unknown model: {model_name}")
    model = model.to(device)

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min',
                                                     factor=0.5, patience=5)

    best_val_loss = float('inf')
    patience_counter = 0
    history = {'train_loss': [], 'val_loss': [], 'val_mae': []}

    for epoch in range(epochs):
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_results = evaluate(model, val_loader, criterion, device)
        scheduler.step(val_results['loss'])

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_results['loss'])
        history['val_mae'].append(val_results['mae'])

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} - Train: {train_loss:.4f}, "
                  f"Val: {val_results['loss']:.4f}, Val MAE: {val_results['mae']:.2f}")

        if val_results['loss'] < best_val_loss:
            best_val_loss = val_results['loss']
            patience_counter = 0
            checkpoint_path = output_path / f"{model_name}_shared_best.pt"
            torch.save({
                'model_name': model_name,
                'regime': 'shared',
                'view_names': view_names,
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'val_loss': val_results['loss'],
                'val_mae': val_results['mae'],
            }, checkpoint_path)
        else:
            patience_counter += 1
            if patience_counter >= early_stop_patience:
                print(f"Early stopping at epoch {epoch+1}")
                break

    # 逐视图测试评估（单视图质量控制指标，防 over-invariance）
    best = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(best['model_state_dict'])

    per_view_metrics = {}
    for view_name, ds in test_by_view.items():
        loader = DataLoader(ds, batch_size=batch_size, shuffle=False,
                            num_workers=0, pin_memory=pin)
        res = evaluate(model, loader, criterion, device)
        per_view_metrics[view_name] = {
            'mae': float(res['mae']),
            'rmse': float(res['rmse'])
        }
        print(f"  Test [{view_name}] MAE: {res['mae']:.2f}  RMSE: {res['rmse']:.2f}")

    result = {
        'model_name': model_name,
        'regime': 'shared',
        'view_names': view_names,
        'config': {
            'n_sensors': n_sensors,
            'batch_size': batch_size,
            'epochs_requested': epochs,
            'epochs_completed': len(history['train_loss']),
            'learning_rate': lr,
            'early_stop_patience': early_stop_patience,
            'validation_fraction': val_fraction,
            'train_units': n_fit,
            'validation_units': n_val,
            'train_windows': len(train_dataset),
            'validation_windows': len(val_dataset),
            'view_masks': {
                name: list(views_data['views'][name]['mask']) for name in view_names
            },
        },
        'best_epoch': best['epoch'],
        'best_val_loss': float(best['val_loss']),
        'best_val_mae': float(best['val_mae']),
        'per_view_test_metrics': per_view_metrics,
        'seed': seed,
        'history': {k: [float(v) for v in vals] for k, vals in history.items()},
        'checkpoint_path': str(checkpoint_path),
    }

    result_file = output_path / f"{model_name}_shared_results.json"
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Shared-model training complete: {checkpoint_path}")
    return result


if __name__ == "__main__":
    device = os.getenv('CMAPSS_DEVICE') or ('cuda:0' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    views_file = os.getenv('CMAPSS_VIEWS_FILE',
                           './cmapss_views/cmapss_views_random_seed42.pkl')
    with open(views_file, 'rb') as f:
        views_data = pickle.load(f)

    n_sensors = len(views_data['active_sensors'])
    print(f"Active sensors: {n_sensors}")

    # 与 specialist 版本相同的三个视图
    view_names = ['full', 'view_1', 'view_2']

    model_names = [os.getenv('CMAPSS_MODEL_NAME')] if os.getenv('CMAPSS_MODEL_NAME') \
        else ['PROP-DIRECT', 'B-STDPROB']
    batch_size = int(os.getenv('CMAPSS_BATCH_SIZE', '256'))
    epochs = int(os.getenv('CMAPSS_EPOCHS', '100'))
    lr = float(os.getenv('CMAPSS_LR', '0.001'))
    patience = int(os.getenv('CMAPSS_PATIENCE', '15'))
    seed = int(os.getenv('CMAPSS_SEED', '42'))
    output_dir = os.getenv('CMAPSS_SHARED_OUTPUT_DIR', './cmapss_models_shared')

    for model_name in model_names:
        train_shared_model(
            model_name=model_name,
            views_data=views_data,
            view_names=view_names,
            n_sensors=n_sensors,
            device=device,
            batch_size=batch_size,
            epochs=epochs,
            lr=lr,
            early_stop_patience=patience,
            output_dir=output_dir,
            seed=seed,
        )

    print("\n" + "="*60)
    print("  下一步：运行 evaluate_cmapss_geometry_shared.py")
    print("  计算 shared-model 的跨视图几何一致性（应与 specialist 结果对比）")
    print("="*60)

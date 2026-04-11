#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 5: 探索的データ解析（EDA）

入力:
- data/interim/analysis_dataset_full.csv

出力:
- results/reports/eda_summary.md
- results/figures/eda_correlation_heatmap.png
- results/figures/eda_distributions.png
- results/figures/eda_bivariate_scatter.png
- results/tables/table1_descriptive_stats.csv
- results/tables/correlation_matrix.csv
- results/tables/vif_multicollinearity.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor

# ndb_library からフォント設定を読み込み
import sys
sys.path.append(str(Path(__file__).resolve().parents[3] / "src"))
from ndb_library.viz import set_japanese_font

# プロジェクトルート（NDB_Research_Hub）
project_root = Path(__file__).resolve().parents[3]

# ロガー設定
log_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "05_exploratory_analysis.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 日本語フォント設定
set_japanese_font()


def load_data():
    """分析データを読み込み"""
    file_path = project_root / "projects/NDB_XXX_slope_diabetes/data/interim/analysis_dataset_full.csv"

    df = pd.read_csv(file_path, encoding='utf-8-sig')
    logger.info(f"データ読み込み: {len(df)}都道府県 × {len(df.columns)}変数")
    logger.info(f"カラム: {df.columns.tolist()}")

    return df


def descriptive_statistics(df):
    """
    記述統計を計算

    Parameters:
    -----------
    df : pd.DataFrame
        分析データ

    Returns:
    --------
    pd.DataFrame
        記述統計表
    """
    logger.info("\n--- 記述統計 ---")

    # 数値型カラムのみ抽出
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # slope_data_available は除外（全て1のため）
    if 'slope_data_available' in numeric_cols:
        numeric_cols.remove('slope_data_available')

    # 記述統計を計算
    desc_stats = df[numeric_cols].describe().T

    # N, Mean, SD, Min, Max を抽出
    table1 = pd.DataFrame({
        'Variable': desc_stats.index,
        'N': desc_stats['count'].astype(int),
        'Mean': desc_stats['mean'].round(2),
        'SD': desc_stats['std'].round(2),
        'Min': desc_stats['min'].round(2),
        'Max': desc_stats['max'].round(2)
    })

    logger.info(f"\n{table1.to_string(index=False)}")

    return table1


def correlation_analysis(df):
    """
    相関分析

    Parameters:
    -----------
    df : pd.DataFrame
        分析データ

    Returns:
    --------
    pd.DataFrame
        相関マトリックス
    """
    logger.info("\n--- 相関分析 ---")

    # 主要変数のみ抽出
    key_vars = [
        'hba1c_mean',
        'bmi_obesity_rate',
        'waist_mean',
        'triglycerides_mean',
        'avg_slope_weighted',
        'walkability_index',
        'pop_density',
        'did_ratio',
        'aging_rate',
        'income_per_capita',
        'unemployment_rate',
        'exercise_habit_rate',
        'college_graduate_rate'
    ]

    df_corr = df[key_vars].copy()

    # 相関マトリックス計算
    corr_matrix = df_corr.corr()

    # 高い相関（|r| > 0.7）を警告
    logger.info("\n高相関ペア（|r| > 0.7）:")
    high_corr = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) > 0.7:
                var1 = corr_matrix.columns[i]
                var2 = corr_matrix.columns[j]
                r_val = corr_matrix.iloc[i, j]
                logger.info(f"  {var1} vs {var2}: r={r_val:.3f}")
                high_corr.append((var1, var2, r_val))

    if len(high_corr) == 0:
        logger.info("  なし（多重共線性のリスクは低い）")

    return corr_matrix


def calculate_vif(df):
    """
    VIF（多重共線性）を計算

    Parameters:
    -----------
    df : pd.DataFrame
        分析データ

    Returns:
    --------
    pd.DataFrame
        VIF表
    """
    logger.info("\n--- VIF（多重共線性）チェック ---")

    # 説明変数候補
    predictors = [
        'avg_slope_weighted',
        'walkability_index',
        'aging_rate',
        'income_per_capita',
        'unemployment_rate',
        'exercise_habit_rate',
        'college_graduate_rate'
    ]

    # 欠損値除外
    df_vif = df[predictors].dropna()

    # VIF計算
    vif_data = pd.DataFrame()
    vif_data['Variable'] = predictors
    vif_data['VIF'] = [variance_inflation_factor(df_vif.values, i) for i in range(len(predictors))]

    logger.info(f"\n{vif_data.to_string(index=False)}")

    # VIF > 5.0 を警告
    high_vif = vif_data[vif_data['VIF'] > 5.0]
    if len(high_vif) > 0:
        logger.warning(f"\n警告: VIF > 5.0 の変数あり（多重共線性の可能性）:")
        logger.warning(f"\n{high_vif.to_string(index=False)}")
    else:
        logger.info("\n✓ 全変数のVIF < 5.0（多重共線性なし）")

    return vif_data


def plot_correlation_heatmap(corr_matrix, output_dir):
    """相関ヒートマップを作成"""
    logger.info("\n--- 相関ヒートマップ作成 ---")

    fig, ax = plt.subplots(figsize=(12, 10))

    # ヒートマップ
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap='RdBu_r',
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={'label': 'Pearson r'},
        ax=ax
    )

    ax.set_title('相関マトリックス（N=47都道府県）', fontsize=14, pad=20)

    plt.tight_layout()
    output_file = output_dir / "eda_correlation_heatmap.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"相関ヒートマップ保存: {output_file}")


def plot_distributions(df, output_dir):
    """主要変数の分布を可視化"""
    logger.info("\n--- 分布プロット作成 ---")

    # 主要アウトカム変数
    outcome_vars = ['hba1c_mean', 'bmi_obesity_rate', 'waist_mean', 'triglycerides_mean']

    # 主要曝露変数
    exposure_vars = ['avg_slope_weighted', 'walkability_index']

    all_vars = outcome_vars + exposure_vars

    fig, axes = plt.subplots(3, 2, figsize=(12, 12))
    axes = axes.flatten()

    for i, var in enumerate(all_vars):
        ax = axes[i]

        # ヒストグラム + KDE
        ax.hist(df[var].dropna(), bins=15, alpha=0.6, color='steelblue', edgecolor='black')
        ax2 = ax.twinx()
        df[var].dropna().plot(kind='kde', ax=ax2, color='red', linewidth=2)

        # Shapiro-Wilk検定（正規性）
        stat, p_value = stats.shapiro(df[var].dropna())
        normality_text = f"Shapiro-Wilk: p={p_value:.4f}"

        ax.set_xlabel(var, fontsize=10)
        ax.set_ylabel('度数', fontsize=10)
        ax2.set_ylabel('密度', fontsize=10)
        ax.set_title(f'{var}\n{normality_text}', fontsize=11)
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    output_file = output_dir / "eda_distributions.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"分布プロット保存: {output_file}")


def plot_bivariate_scatter(df, output_dir):
    """二変量散布図を作成"""
    logger.info("\n--- 二変量散布図作成 ---")

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # 1. HbA1c vs Slope
    ax1 = axes[0, 0]
    ax1.scatter(df['avg_slope_weighted'], df['hba1c_mean'], alpha=0.6, s=80, color='steelblue')

    # 回帰直線
    z = np.polyfit(df['avg_slope_weighted'].dropna(), df['hba1c_mean'].dropna(), 1)
    p = np.poly1d(z)
    x_line = np.linspace(df['avg_slope_weighted'].min(), df['avg_slope_weighted'].max(), 100)
    ax1.plot(x_line, p(x_line), "r--", linewidth=2, label=f'y={z[0]:.4f}x+{z[1]:.2f}')

    # 相関係数
    r, p_val = stats.pearsonr(df['avg_slope_weighted'].dropna(), df['hba1c_mean'].dropna())
    ax1.text(0.05, 0.95, f'r={r:.3f}, p={p_val:.4f}', transform=ax1.transAxes,
             fontsize=11, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax1.set_xlabel('地形傾斜度（°）', fontsize=11)
    ax1.set_ylabel('HbA1c平均値（%）', fontsize=11)
    ax1.set_title('HbA1c vs 地形傾斜度', fontsize=12, pad=10)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # 2. HbA1c vs Walkability
    ax2 = axes[0, 1]
    ax2.scatter(df['walkability_index'], df['hba1c_mean'], alpha=0.6, s=80, color='darkgreen')

    z = np.polyfit(df['walkability_index'].dropna(), df['hba1c_mean'].dropna(), 1)
    p = np.poly1d(z)
    x_line = np.linspace(df['walkability_index'].min(), df['walkability_index'].max(), 100)
    ax2.plot(x_line, p(x_line), "r--", linewidth=2, label=f'y={z[0]:.4f}x+{z[1]:.2f}')

    r, p_val = stats.pearsonr(df['walkability_index'].dropna(), df['hba1c_mean'].dropna())
    ax2.text(0.05, 0.95, f'r={r:.3f}, p={p_val:.4f}', transform=ax2.transAxes,
             fontsize=11, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax2.set_xlabel('Walkability Index', fontsize=11)
    ax2.set_ylabel('HbA1c平均値（%）', fontsize=11)
    ax2.set_title('HbA1c vs Walkability Index', fontsize=12, pad=10)
    ax2.legend()
    ax2.grid(alpha=0.3)

    # 3. BMI vs Slope
    ax3 = axes[1, 0]
    ax3.scatter(df['avg_slope_weighted'], df['bmi_obesity_rate'], alpha=0.6, s=80, color='coral')

    z = np.polyfit(df['avg_slope_weighted'].dropna(), df['bmi_obesity_rate'].dropna(), 1)
    p = np.poly1d(z)
    x_line = np.linspace(df['avg_slope_weighted'].min(), df['avg_slope_weighted'].max(), 100)
    ax3.plot(x_line, p(x_line), "r--", linewidth=2, label=f'y={z[0]:.4f}x+{z[1]:.2f}')

    r, p_val = stats.pearsonr(df['avg_slope_weighted'].dropna(), df['bmi_obesity_rate'].dropna())
    ax3.text(0.05, 0.95, f'r={r:.3f}, p={p_val:.4f}', transform=ax3.transAxes,
             fontsize=11, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax3.set_xlabel('地形傾斜度（°）', fontsize=11)
    ax3.set_ylabel('BMI肥満率（%）', fontsize=11)
    ax3.set_title('BMI肥満率 vs 地形傾斜度', fontsize=12, pad=10)
    ax3.legend()
    ax3.grid(alpha=0.3)

    # 4. BMI vs Walkability
    ax4 = axes[1, 1]
    ax4.scatter(df['walkability_index'], df['bmi_obesity_rate'], alpha=0.6, s=80, color='purple')

    z = np.polyfit(df['walkability_index'].dropna(), df['bmi_obesity_rate'].dropna(), 1)
    p = np.poly1d(z)
    x_line = np.linspace(df['walkability_index'].min(), df['walkability_index'].max(), 100)
    ax4.plot(x_line, p(x_line), "r--", linewidth=2, label=f'y={z[0]:.4f}x+{z[1]:.2f}')

    r, p_val = stats.pearsonr(df['walkability_index'].dropna(), df['bmi_obesity_rate'].dropna())
    ax4.text(0.05, 0.95, f'r={r:.3f}, p={p_val:.4f}', transform=ax4.transAxes,
             fontsize=11, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax4.set_xlabel('Walkability Index', fontsize=11)
    ax4.set_ylabel('BMI肥満率（%）', fontsize=11)
    ax4.set_title('BMI肥満率 vs Walkability Index', fontsize=12, pad=10)
    ax4.legend()
    ax4.grid(alpha=0.3)

    plt.tight_layout()
    output_file = output_dir / "eda_bivariate_scatter.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"二変量散布図保存: {output_file}")


def generate_eda_report(table1, corr_matrix, vif_data, output_dir):
    """EDAレポートをMarkdown形式で生成"""
    logger.info("\n--- EDAレポート生成 ---")

    report = f"""# Phase 5: 探索的データ解析レポート

## 1. データ概要

- **N**: 47都道府県
- **変数数**: 22変数
- **欠損データ**: なし（全変数完全データ）

## 2. 記述統計（Table 1）

{table1.to_markdown(index=False)}

## 3. 相関分析

### 主要な相関

**アウトカム vs 曝露変数:**
- HbA1c vs Slope: r={corr_matrix.loc['hba1c_mean', 'avg_slope_weighted']:.3f}
- HbA1c vs Walkability: r={corr_matrix.loc['hba1c_mean', 'walkability_index']:.3f}
- BMI vs Slope: r={corr_matrix.loc['bmi_obesity_rate', 'avg_slope_weighted']:.3f}
- BMI vs Walkability: r={corr_matrix.loc['bmi_obesity_rate', 'walkability_index']:.3f}

### 多重共線性チェック（VIF）

{vif_data.to_markdown(index=False)}

**判定**: {"VIF < 5.0（多重共線性なし）" if vif_data['VIF'].max() < 5.0 else "VIF > 5.0の変数あり（要注意）"}

## 4. 正規性検定

主要アウトカム変数のShapiro-Wilk検定結果は分布プロットを参照。

## 5. 次のステップ

- **Phase 6a**: OLS回帰分析（Walkability & Slope models）
- **Phase 6b**: 空間回帰分析（Moran's I検定 → SLM/SEM）

## ファイル出力

- 相関ヒートマップ: `results/figures/eda_correlation_heatmap.png`
- 分布プロット: `results/figures/eda_distributions.png`
- 二変量散布図: `results/figures/eda_bivariate_scatter.png`
"""

    output_file = output_dir / "eda_summary.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"EDAレポート保存: {output_file}")


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 5: 探索的データ解析開始")
    logger.info("=" * 60)

    try:
        # 出力ディレクトリ作成
        figures_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/figures"
        tables_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/tables"
        reports_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/reports"

        figures_dir.mkdir(parents=True, exist_ok=True)
        tables_dir.mkdir(parents=True, exist_ok=True)
        reports_dir.mkdir(parents=True, exist_ok=True)

        # 1. データ読み込み
        logger.info("\n--- ステップ1: データ読み込み ---")
        df = load_data()

        # 2. 記述統計
        logger.info("\n--- ステップ2: 記述統計 ---")
        table1 = descriptive_statistics(df)
        table1.to_csv(tables_dir / "table1_descriptive_stats.csv", index=False, encoding='utf-8-sig')

        # 3. 相関分析
        logger.info("\n--- ステップ3: 相関分析 ---")
        corr_matrix = correlation_analysis(df)
        corr_matrix.to_csv(tables_dir / "correlation_matrix.csv", encoding='utf-8-sig')

        # 4. VIF計算
        logger.info("\n--- ステップ4: VIF計算 ---")
        vif_data = calculate_vif(df)
        vif_data.to_csv(tables_dir / "vif_multicollinearity.csv", index=False, encoding='utf-8-sig')

        # 5. 可視化
        logger.info("\n--- ステップ5: 可視化 ---")
        plot_correlation_heatmap(corr_matrix, figures_dir)
        plot_distributions(df, figures_dir)
        plot_bivariate_scatter(df, figures_dir)

        # 6. EDAレポート生成
        logger.info("\n--- ステップ6: EDAレポート生成 ---")
        generate_eda_report(table1, corr_matrix, vif_data, reports_dir)

        logger.info("\n" + "=" * 60)
        logger.info("Phase 5 処理完了！")
        logger.info("=" * 60)

        logger.info("\n【次のステップ】")
        logger.info("Phase 6a: OLS回帰分析")
        logger.info("  - Model 1: Walkability → HbA1c")
        logger.info("  - Model 2: Slope → HbA1c")
        logger.info("  - Model 3: Combined (Slope + Walkability)")

    except Exception as e:
        logger.error(f"エラー発生: {e}")
        raise


if __name__ == "__main__":
    main()

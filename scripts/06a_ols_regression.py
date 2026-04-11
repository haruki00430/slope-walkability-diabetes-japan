#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 6a: OLS回帰分析（Walkability & Slope models）

入力:
- data/interim/analysis_dataset_full.csv

出力:
- results/tables/ols_model1_walkability_hba1c.csv
- results/tables/ols_model2_slope_hba1c.csv
- results/tables/ols_model3_combined_hba1c.csv
- results/tables/ols_summary_all_outcomes.csv
- results/figures/ols_diagnostics.png
- results/reports/ols_regression_results.md
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats as scipy_stats

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
        logging.FileHandler(log_dir / "06a_ols_regression.log", encoding="utf-8"),
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
    return df


def run_ols_regression(df, outcome, exposure, covariates):
    """
    OLS回帰分析を実行

    Parameters:
    -----------
    df : pd.DataFrame
        分析データ
    outcome : str
        従属変数名
    exposure : str or list
        独立変数名（単一または複数）
    covariates : list
        調整変数リスト

    Returns:
    --------
    sm.regression.linear_model.RegressionResultsWrapper
        回帰結果
    """
    # 独立変数リスト作成
    if isinstance(exposure, str):
        predictors = [exposure] + covariates
    else:
        predictors = exposure + covariates

    # 欠損値除外
    analysis_vars = [outcome] + predictors
    df_analysis = df[analysis_vars].dropna()

    logger.info(f"\n解析対象: N={len(df_analysis)}都道府県")
    logger.info(f"従属変数: {outcome}")
    logger.info(f"独立変数: {predictors}")

    # Y, X 準備
    y = df_analysis[outcome]
    X = df_analysis[predictors]
    X = sm.add_constant(X)  # 切片項追加

    # OLS実行
    model = sm.OLS(y, X)
    results = model.fit()

    return results, df_analysis


def calculate_vif_for_model(df, predictors):
    """モデルのVIFを計算"""
    df_vif = df[predictors].dropna()
    vif_data = pd.DataFrame()
    vif_data['Variable'] = predictors
    vif_data['VIF'] = [variance_inflation_factor(df_vif.values, i) for i in range(len(predictors))]
    return vif_data


def extract_regression_table(results, model_name):
    """
    回帰結果を表形式で抽出

    Returns:
    --------
    pd.DataFrame
        β, SE, t, p, 95%CI を含む表
    """
    summary = results.summary2().tables[1]

    table = pd.DataFrame({
        'Model': model_name,
        'Variable': summary.index,
        'Beta': summary['Coef.'].round(4),
        'SE': summary['Std.Err.'].round(4),
        't': summary['t'].round(3),
        'p': summary['P>|t|'].round(4),
        'CI_lower': summary['[0.025'].round(4),
        'CI_upper': summary['0.975]'].round(4)
    })

    return table


def run_diagnostics(results, df_analysis, outcome):
    """
    回帰診断を実行

    Returns:
    --------
    dict
        診断結果（VIF, 正規性検定, 等分散性検定）
    """
    diagnostics = {}

    # 1. 残差の正規性（Shapiro-Wilk検定）
    residuals = results.resid
    shapiro_stat, shapiro_p = scipy_stats.shapiro(residuals)
    diagnostics['shapiro_stat'] = shapiro_stat
    diagnostics['shapiro_p'] = shapiro_p

    # 2. 等分散性（Breusch-Pagan検定）
    from statsmodels.stats.diagnostic import het_breuschpagan
    bp_stat, bp_p, _, _ = het_breuschpagan(residuals, results.model.exog)
    diagnostics['bp_stat'] = bp_stat
    diagnostics['bp_p'] = bp_p

    # 3. 影響力のある点（Cook's Distance）
    influence = results.get_influence()
    cooks_d = influence.cooks_distance[0]
    diagnostics['max_cooks_d'] = cooks_d.max()
    diagnostics['influential_points'] = (cooks_d > 4 / len(df_analysis)).sum()

    return diagnostics


def plot_diagnostics(results_list, outcome_names, output_dir):
    """
    回帰診断プロットを作成

    Parameters:
    -----------
    results_list : list of RegressionResults
        回帰結果リスト
    outcome_names : list of str
        アウトカム名リスト
    output_dir : Path
        出力ディレクトリ
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    for i, (results, outcome_name) in enumerate(zip(results_list[:4], outcome_names[:4])):
        ax = axes.flatten()[i]

        # Residuals vs Fitted
        fitted = results.fittedvalues
        residuals = results.resid

        ax.scatter(fitted, residuals, alpha=0.6, s=60)
        ax.axhline(y=0, color='red', linestyle='--', linewidth=2)
        ax.set_xlabel('Fitted values', fontsize=10)
        ax.set_ylabel('Residuals', fontsize=10)
        ax.set_title(f'{outcome_name}: Residuals vs Fitted', fontsize=11)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    output_file = output_dir / "ols_diagnostics.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"診断プロット保存: {output_file}")


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 6a: OLS回帰分析開始")
    logger.info("=" * 60)

    try:
        # 出力ディレクトリ作成
        tables_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/tables"
        figures_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/figures"
        reports_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/reports"

        tables_dir.mkdir(parents=True, exist_ok=True)
        figures_dir.mkdir(parents=True, exist_ok=True)
        reports_dir.mkdir(parents=True, exist_ok=True)

        # 1. データ読み込み
        logger.info("\n--- ステップ1: データ読み込み ---")
        df = load_data()

        # 調整変数（Option 1: aging_rate + income_per_capita のみ）
        covariates = ['aging_rate', 'income_per_capita']

        # アウトカム変数
        outcomes = {
            'hba1c_mean': 'HbA1c平均値',
            'bmi_obesity_rate': 'BMI肥満率',
            'waist_mean': '腹囲平均値',
            'triglycerides_mean': '中性脂肪平均値'
        }

        all_tables = []
        all_diagnostics = []
        results_for_plot = []

        for outcome_var, outcome_label in outcomes.items():
            logger.info("\n" + "=" * 60)
            logger.info(f"アウトカム: {outcome_label} ({outcome_var})")
            logger.info("=" * 60)

            # Model 1: Walkability → Outcome
            logger.info("\n--- Model 1: Walkability → Outcome ---")
            results1, df_analysis1 = run_ols_regression(df, outcome_var, 'walkability_index', covariates)
            logger.info(f"\nR²={results1.rsquared:.4f}, Adjusted R²={results1.rsquared_adj:.4f}")
            logger.info(f"F-statistic={results1.fvalue:.3f}, p={results1.f_pvalue:.4f}")

            table1 = extract_regression_table(results1, f"{outcome_label}_Model1_Walkability")
            all_tables.append(table1)

            # VIFチェック
            vif1 = calculate_vif_for_model(df, ['walkability_index'] + covariates)
            logger.info(f"\nVIF:\n{vif1.to_string(index=False)}")

            # 診断
            diag1 = run_diagnostics(results1, df_analysis1, outcome_var)
            logger.info(f"\n診断結果:")
            logger.info(f"  Shapiro-Wilk (残差正規性): p={diag1['shapiro_p']:.4f}")
            logger.info(f"  Breusch-Pagan (等分散性): p={diag1['bp_p']:.4f}")
            logger.info(f"  Max Cook's D: {diag1['max_cooks_d']:.4f}")
            logger.info(f"  Influential points (Cook's D > 4/N): {diag1['influential_points']}")

            all_diagnostics.append({
                'Model': f"{outcome_label}_Model1_Walkability",
                'R2': results1.rsquared,
                'Adj_R2': results1.rsquared_adj,
                'F': results1.fvalue,
                'F_p': results1.f_pvalue,
                'Shapiro_p': diag1['shapiro_p'],
                'BP_p': diag1['bp_p'],
                'Max_Cooks_D': diag1['max_cooks_d'],
                'Influential_points': diag1['influential_points']
            })

            # Model 2: Slope → Outcome
            logger.info("\n--- Model 2: Slope → Outcome ---")
            results2, df_analysis2 = run_ols_regression(df, outcome_var, 'avg_slope_weighted', covariates)
            logger.info(f"\nR²={results2.rsquared:.4f}, Adjusted R²={results2.rsquared_adj:.4f}")
            logger.info(f"F-statistic={results2.fvalue:.3f}, p={results2.f_pvalue:.4f}")

            table2 = extract_regression_table(results2, f"{outcome_label}_Model2_Slope")
            all_tables.append(table2)

            # VIFチェック
            vif2 = calculate_vif_for_model(df, ['avg_slope_weighted'] + covariates)
            logger.info(f"\nVIF:\n{vif2.to_string(index=False)}")

            # 診断
            diag2 = run_diagnostics(results2, df_analysis2, outcome_var)
            logger.info(f"\n診断結果:")
            logger.info(f"  Shapiro-Wilk (残差正規性): p={diag2['shapiro_p']:.4f}")
            logger.info(f"  Breusch-Pagan (等分散性): p={diag2['bp_p']:.4f}")
            logger.info(f"  Max Cook's D: {diag2['max_cooks_d']:.4f}")

            all_diagnostics.append({
                'Model': f"{outcome_label}_Model2_Slope",
                'R2': results2.rsquared,
                'Adj_R2': results2.rsquared_adj,
                'F': results2.fvalue,
                'F_p': results2.f_pvalue,
                'Shapiro_p': diag2['shapiro_p'],
                'BP_p': diag2['bp_p'],
                'Max_Cooks_D': diag2['max_cooks_d'],
                'Influential_points': diag2['influential_points']
            })

            # Model 3: Combined (Slope + Walkability)
            logger.info("\n--- Model 3: Combined (Slope + Walkability) ---")
            results3, df_analysis3 = run_ols_regression(df, outcome_var, ['avg_slope_weighted', 'walkability_index'], covariates)
            logger.info(f"\nR²={results3.rsquared:.4f}, Adjusted R²={results3.rsquared_adj:.4f}")
            logger.info(f"F-statistic={results3.fvalue:.3f}, p={results3.f_pvalue:.4f}")

            table3 = extract_regression_table(results3, f"{outcome_label}_Model3_Combined")
            all_tables.append(table3)

            # VIFチェック
            vif3 = calculate_vif_for_model(df, ['avg_slope_weighted', 'walkability_index'] + covariates)
            logger.info(f"\nVIF:\n{vif3.to_string(index=False)}")

            # 診断
            diag3 = run_diagnostics(results3, df_analysis3, outcome_var)
            logger.info(f"\n診断結果:")
            logger.info(f"  Shapiro-Wilk (残差正規性): p={diag3['shapiro_p']:.4f}")
            logger.info(f"  Breusch-Pagan (等分散性): p={diag3['bp_p']:.4f}")
            logger.info(f"  Max Cook's D: {diag3['max_cooks_d']:.4f}")

            all_diagnostics.append({
                'Model': f"{outcome_label}_Model3_Combined",
                'R2': results3.rsquared,
                'Adj_R2': results3.rsquared_adj,
                'F': results3.fvalue,
                'F_p': results3.f_pvalue,
                'Shapiro_p': diag3['shapiro_p'],
                'BP_p': diag3['bp_p'],
                'Max_Cooks_D': diag3['max_cooks_d'],
                'Influential_points': diag3['influential_points']
            })

            # プロット用に保存
            if outcome_var == 'hba1c_mean':
                results_for_plot.append((results3, outcome_label))
            elif outcome_var == 'bmi_obesity_rate':
                results_for_plot.append((results3, outcome_label))
            elif outcome_var == 'waist_mean':
                results_for_plot.append((results3, outcome_label))
            elif outcome_var == 'triglycerides_mean':
                results_for_plot.append((results3, outcome_label))

        # 2. 結果の保存
        logger.info("\n--- ステップ2: 結果の保存 ---")

        # 全モデルの回帰係数表を統合
        df_all_tables = pd.concat(all_tables, ignore_index=True)
        df_all_tables.to_csv(tables_dir / "ols_summary_all_outcomes.csv", index=False, encoding='utf-8-sig')
        logger.info(f"回帰係数表保存: {tables_dir / 'ols_summary_all_outcomes.csv'}")

        # 診断結果を保存
        df_diagnostics = pd.DataFrame(all_diagnostics)
        df_diagnostics.to_csv(tables_dir / "ols_diagnostics_summary.csv", index=False, encoding='utf-8-sig')
        logger.info(f"診断結果保存: {tables_dir / 'ols_diagnostics_summary.csv'}")

        # 3. 診断プロット作成
        logger.info("\n--- ステップ3: 診断プロット作成 ---")
        plot_diagnostics(
            [r for r, _ in results_for_plot],
            [label for _, label in results_for_plot],
            figures_dir
        )

        logger.info("\n" + "=" * 60)
        logger.info("Phase 6a 処理完了！")
        logger.info("=" * 60)

        logger.info("\n【次のステップ】")
        logger.info("Phase 6b: 空間回帰分析（Moran's I検定 → SLM/SEM）")
        logger.info("  - OLS残差の空間的自己相関を検定")
        logger.info("  - 有意な場合のみ空間回帰モデルを適用")

    except Exception as e:
        logger.error(f"エラー発生: {e}")
        raise


if __name__ == "__main__":
    main()

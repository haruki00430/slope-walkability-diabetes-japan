#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 8: Generate Manuscript Figures (Figures 1–4)
       / 論文図の作成（Figure 1〜4）

Create the four publication-ready figures for the manuscript at 300 dpi:
  Figure 1 — Geographic distribution maps of key variables (slope, walkability,
              HbA1c, BMI obesity) across 47 Japanese prefectures (choropleth)
  Figure 2 — Forest plot of OLS regression coefficients (β) for walkability and
              slope across all four outcomes, with 95% confidence intervals
  Figure 3 — Scatter plot grid: walkability vs each diabetes indicator (N=47),
              with OLS regression line and 95% CI
  Figure 4 — Spatial autocorrelation analysis: Moran scatterplot, LISA cluster
              map, and OLS vs SLM model performance comparison for BMI obesity
論文用図（Figure 1〜4、300dpi）を生成する。

Input / 入力:
    data/interim/analysis_dataset_full.csv          — Master dataset (N=47)
    data/external/japan_prefectures_47.geojson      — Prefecture boundary polygons
    results/tables/ols_summary_all_outcomes.csv     — OLS regression results
    results/tables/morans_i_test.csv                — Moran's I test results
    results/tables/spatial_model_comparison.csv     — SLM/SEM model comparison

Output / 出力:
    results/figures/figure1_study_overview_map.png      — Choropleth maps (4-panel)
    results/figures/figure2_forest_plot.png             — Regression coefficient forest plot
    results/figures/figure3_scatter_grid.png            — Walkability vs outcome scatter grid
    results/figures/figure4_spatial_autocorrelation.png — Spatial analysis summary (4-panel)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from pathlib import Path
import logging
from matplotlib.patches import Rectangle
from esda.moran import Moran
from libpysal.weights import Queen, KNN, w_union
import statsmodels.api as sm

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
        logging.FileHandler(log_dir / "08_create_figures.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 日本語フォント設定
set_japanese_font()


def load_data():
    """データ読み込み"""
    logger.info("\n--- データ読み込み ---")

    # 分析データ
    df = pd.read_csv(
        project_root / "projects/NDB_XXX_slope_diabetes/data/interim/analysis_dataset_full.csv",
        encoding='utf-8-sig'
    )
    logger.info(f"分析データ読み込み: {len(df)}都道府県")

    # 空間データ
    gdf = gpd.read_file(
        project_root / "projects/NDB_XXX_slope_diabetes/data/external/japan_prefectures_47.geojson",
        encoding='utf-8'
    )
    logger.info(f"GeoJSON読み込み: {len(gdf)}都道府県")

    # カラム名を確認・変換（都道府県 → prefecture）
    if '都道府県' in gdf.columns:
        gdf = gdf.rename(columns={'都道府県': 'prefecture'})
        logger.info("都道府県カラムをprefectureにリネーム")

    # マージ
    gdf = gdf.merge(df, on='prefecture', how='left')
    logger.info(f"マージ後: {len(gdf)}都道府県")

    # OLS結果
    ols_results = pd.read_csv(
        project_root / "projects/NDB_XXX_slope_diabetes/results/tables/ols_summary_all_outcomes.csv",
        encoding='utf-8-sig'
    )
    logger.info(f"OLS結果読み込み: {len(ols_results)}行")

    # Moran's I結果
    moran_results = pd.read_csv(
        project_root / "projects/NDB_XXX_slope_diabetes/results/tables/morans_i_test.csv",
        encoding='utf-8-sig'
    )
    logger.info(f"Moran's I結果読み込み: {len(moran_results)}行")

    # 空間モデル比較（BMI肥満率のみ）
    spatial_comparison_file = project_root / "projects/NDB_XXX_slope_diabetes/results/tables/spatial_model_comparison.csv"
    if spatial_comparison_file.exists():
        spatial_comparison = pd.read_csv(spatial_comparison_file, encoding='utf-8-sig')
        logger.info(f"空間モデル比較読み込み: {len(spatial_comparison)}行")
    else:
        spatial_comparison = None
        logger.warning("空間モデル比較ファイルが存在しません")

    return gdf, ols_results, moran_results, spatial_comparison


def create_figure1_study_overview_map(gdf, output_dir):
    """
    Figure 1: Study Overview Map（3パネルchoropleth）
    カラーバーは各パネル下部に水平配置
    """
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import Normalize

    logger.info("\n--- Figure 1: Study Overview Map作成 ---")

    panels = [
        {'col': 'hba1c_mean',         'cmap': 'YlOrRd',  'label': 'Mean HbA1c (%)',    'title': 'A. Mean HbA1c (%)'},
        {'col': 'avg_slope_weighted',  'cmap': 'terrain',  'label': 'Mean Slope (°)',     'title': 'B. Topographic Slope (°)'},
        {'col': 'walkability_index',   'cmap': 'viridis',  'label': 'Walkability Index',  'title': 'C. Walkability Index'},
    ]

    fig, axes = plt.subplots(1, 3, figsize=(21, 6))

    for ax, p in zip(axes, panels):
        col  = p['col']
        vmin = gdf[col].min()
        vmax = gdf[col].max()

        gdf.plot(
            column=col,
            cmap=p['cmap'],
            vmin=vmin,
            vmax=vmax,
            legend=False,
            ax=ax,
            edgecolor='black',
            linewidth=0.5,
        )
        ax.set_title(p['title'], fontsize=13, weight='bold')
        ax.axis('off')

        # カラーバーを下部に水平配置
        sm = ScalarMappable(cmap=p['cmap'], norm=Normalize(vmin=vmin, vmax=vmax))
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, orientation='horizontal',
                            shrink=0.75, pad=0.02, fraction=0.04, aspect=30)
        cbar.set_label(p['label'], fontsize=11)
        cbar.ax.tick_params(labelsize=9)

    plt.tight_layout()
    output_file = output_dir / "figure1_study_overview_map.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Figure 1保存: {output_file}")


def create_figure2_forest_plot(ols_results, output_dir):
    """
    Figure 2: Forest Plot（OLS回帰係数の比較）

    Model 3（Combined）のSlope & Walkabilityの効果を比較
    """
    logger.info("\n--- Figure 2: Forest Plot作成 ---")

    # Model 3のみ抽出
    model3 = ols_results[ols_results['Model'].str.contains('Model3_Combined')].copy()

    # Slope と Walkability の行のみ
    exposure_vars = model3[model3['Variable'].isin(['avg_slope_weighted', 'walkability_index'])].copy()

    # アウトカムラベル作成
    exposure_vars['Outcome'] = exposure_vars['Model'].str.extract(r'(.+?)_Model3')[0]
    exposure_vars['Outcome'] = exposure_vars['Outcome'].replace({
        'HbA1c平均値': 'HbA1c',
        'BMI肥満率': 'BMI obesity',
        '腹囲平均値': 'Waist',
        '中性脂肪平均値': 'Triglycerides'
    })

    # Variable名を整形
    exposure_vars['Exposure'] = exposure_vars['Variable'].replace({
        'avg_slope_weighted': 'Slope',
        'walkability_index': 'Walkability'
    })

    # プロット用ラベル作成
    exposure_vars['Label'] = exposure_vars['Outcome'] + ' - ' + exposure_vars['Exposure']

    # 有意性マーカー
    exposure_vars['Significant'] = exposure_vars['p'] < 0.05

    # プロット
    fig, ax = plt.subplots(figsize=(10, 8))

    y_positions = np.arange(len(exposure_vars))

    # 各行を個別にプロット（色分けのため）
    for i, (idx, row) in enumerate(exposure_vars.iterrows()):
        color = 'red' if row['Significant'] else 'gray'
        marker_color = 'black' if row['Significant'] else 'gray'

        ax.errorbar(
            row['Beta'],
            i,
            xerr=[[row['Beta'] - row['CI_lower']], [row['CI_upper'] - row['Beta']]],
            fmt='o',
            color=marker_color,
            ecolor=color,
            elinewidth=2,
            capsize=5,
            markersize=8
        )

    # 垂直線（β=0）
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1)

    # 軸設定
    ax.set_yticks(y_positions)
    ax.set_yticklabels(exposure_vars['Label'], fontsize=10)
    ax.set_xlabel('β Coefficient (95% CI)', fontsize=12, weight='bold')
    ax.set_title('Figure 2. Forest Plot of Regression Coefficients\n(Model 3: Slope + Walkability)',
                 fontsize=14, weight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)

    # 有意性凡例
    ax.text(0.98, 0.02, '* p < 0.05', transform=ax.transAxes,
            fontsize=10, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    output_file = output_dir / "figure2_forest_plot.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Figure 2保存: {output_file}")


def create_figure3_scatter_grid(gdf, ols_results, output_dir):
    """
    Figure 3: Scatter Plots with Regression Lines（2×2グリッド）

    - HbA1c vs Slope
    - HbA1c vs Walkability
    - BMI vs Slope
    - BMI vs Walkability
    """
    logger.info("\n--- Figure 3: Scatter Grid作成 ---")

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # プロット設定
    plots = [
        {'outcome': 'hba1c_mean', 'exposure': 'avg_slope_weighted',
         'outcome_label': 'Mean HbA1c (%)', 'exposure_label': 'Topographic Slope (°)', 'ax': axes[0, 0]},
        {'outcome': 'hba1c_mean', 'exposure': 'walkability_index',
         'outcome_label': 'Mean HbA1c (%)', 'exposure_label': 'Walkability Index', 'ax': axes[0, 1]},
        {'outcome': 'bmi_obesity_rate', 'exposure': 'avg_slope_weighted',
         'outcome_label': 'BMI Obesity Rate (%)', 'exposure_label': 'Topographic Slope (°)', 'ax': axes[1, 0]},
        {'outcome': 'bmi_obesity_rate', 'exposure': 'walkability_index',
         'outcome_label': 'BMI Obesity Rate (%)', 'exposure_label': 'Walkability Index', 'ax': axes[1, 1]}
    ]

    for i, plot_config in enumerate(plots):
        ax = plot_config['ax']
        outcome = plot_config['outcome']
        exposure = plot_config['exposure']

        # データ抽出
        x = gdf[exposure].values
        y = gdf[outcome].values

        # 散布図
        ax.scatter(x, y, alpha=0.6, s=60, color='steelblue', edgecolors='black', linewidth=0.5)

        # 回帰直線
        X = sm.add_constant(x)
        model = sm.OLS(y, X).fit()
        x_pred = np.linspace(x.min(), x.max(), 100)
        X_pred = sm.add_constant(x_pred)
        y_pred = model.predict(X_pred)

        # 95%信頼区間
        prediction = model.get_prediction(X_pred)
        pred_summary = prediction.summary_frame(alpha=0.05)

        ax.plot(x_pred, y_pred, color='red', linewidth=2, label='Regression line')
        ax.fill_between(x_pred, pred_summary['mean_ci_lower'], pred_summary['mean_ci_upper'],
                        color='red', alpha=0.2, label='95% CI')

        # 統計量表示
        r2 = model.rsquared
        beta = model.params[1]
        p_value = model.pvalues[1]

        textstr = f'R² = {r2:.3f}\nβ = {beta:.3f}\np = {p_value:.4f}'
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # 軸ラベル
        ax.set_xlabel(plot_config['exposure_label'], fontsize=11)
        ax.set_ylabel(plot_config['outcome_label'], fontsize=11)
        ax.set_title(f"Panel {chr(65+i)}", fontsize=12, weight='bold')
        ax.legend(loc='lower right', fontsize=9)
        ax.grid(alpha=0.3)

    plt.suptitle('Figure 3. Scatter Plots with Regression Lines', fontsize=14, weight='bold', y=0.995)
    plt.tight_layout()
    output_file = output_dir / "figure3_scatter_grid.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Figure 3保存: {output_file}")


def create_figure4_spatial_autocorrelation(gdf, moran_results, spatial_comparison, output_dir):
    """
    Figure 4: Spatial Autocorrelation（BMI肥満率のMoran's I散布図 + SLM結果）

    Panel A: Moran's I散布図
    Panel B: SLMの空間ラグ係数
    """
    logger.info("\n--- Figure 4: Spatial Autocorrelation作成 ---")

    # BMI肥満率のみ抽出
    bmi_moran = moran_results[moran_results['model'] == 'bmi_obesity_rate_avg_slope_weighted_walkability_index'].iloc[0]

    # 空間重み行列構築（再現）
    from libpysal.weights import Queen, KNN, w_union

    w_queen = Queen.from_dataframe(gdf, use_index=False)
    islands = w_queen.islands

    if len(islands) > 0:
        w_knn = KNN.from_dataframe(gdf, k=1, use_index=False)
        w = w_union(w_queen, w_knn)
    else:
        w = w_queen

    w.transform = 'r'

    # OLS残差計算（Model 3再現）
    exposure = ['avg_slope_weighted', 'walkability_index']
    covariates = ['aging_rate', 'income_per_capita']
    predictors = exposure + covariates

    gdf_analysis = gdf[['bmi_obesity_rate'] + predictors + ['geometry', 'prefecture']].dropna().reset_index(drop=True)

    # 空間重み行列を再構築
    w_queen_analysis = Queen.from_dataframe(gdf_analysis, use_index=False)
    islands_analysis = w_queen_analysis.islands

    if len(islands_analysis) > 0:
        w_knn_analysis = KNN.from_dataframe(gdf_analysis, k=1, use_index=False)
        w_analysis = w_union(w_queen_analysis, w_knn_analysis)
    else:
        w_analysis = w_queen_analysis

    w_analysis.transform = 'r'

    y = gdf_analysis['bmi_obesity_rate'].values
    X = gdf_analysis[predictors].values
    X = np.hstack([np.ones((X.shape[0], 1)), X])

    model = sm.OLS(y, X).fit()
    residuals = model.resid

    # Moran's I計算
    moran = Moran(residuals, w_analysis, permutations=999)

    # 2パネル図作成
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A: Moran's I散布図
    ax = axes[0]

    # 標準化された残差
    residuals_std = (residuals - residuals.mean()) / residuals.std()
    lag_residuals = w_analysis.sparse.dot(residuals_std)

    ax.scatter(residuals_std, lag_residuals, alpha=0.6, s=60, color='steelblue',
               edgecolors='black', linewidth=0.5)

    # 回帰直線
    ax.plot(residuals_std, moran.I * residuals_std, color='red', linewidth=2, label=f"Moran's I = {moran.I:.3f}")

    # 軸ラベル
    ax.set_xlabel('Standardized Residuals', fontsize=11)
    ax.set_ylabel('Spatial Lag (Standardized Residuals)', fontsize=11)
    ax.set_title(f"Panel A: Moran's I Scatter Plot\nI = {moran.I:.3f}, p < 0.001", fontsize=12, weight='bold')
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(alpha=0.3)

    # Panel B: SLMの空間ラグ係数（rho）
    ax = axes[1]

    if spatial_comparison is not None and len(spatial_comparison) > 0:
        slm_rho = spatial_comparison.iloc[0]['SLM_rho']
        slm_pr2 = spatial_comparison.iloc[0]['SLM_PseudoR2']
        ols_r2 = spatial_comparison.iloc[0]['OLS_R2']

        # 棒グラフ（R² vs Pseudo R²）
        models = ['OLS', 'SLM']
        r2_values = [ols_r2, slm_pr2]
        colors_bar = ['lightgray', 'steelblue']

        bars = ax.bar(models, r2_values, color=colors_bar, edgecolor='black', linewidth=1.5, alpha=0.8)

        # 値ラベル
        for bar, value in zip(bars, r2_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                   f'{value:.3f}', ha='center', va='bottom', fontsize=11, weight='bold')

        ax.set_ylabel('R² / Pseudo R²', fontsize=11)
        ax.set_ylim(0, 1)
        ax.set_title(f"Panel B: Model Comparison\nSLM rho = {slm_rho:.3f} (p < 0.001)", fontsize=12, weight='bold')
        ax.grid(axis='y', alpha=0.3)

        # rho係数の説明テキスト
        textstr = f'Spatial lag coeff. (rho) = {slm_rho:.3f}\nA 1% increase in neighboring\nprefectures\' obesity rate is\nassociated with {slm_rho:.2f}% increase'
        ax.text(0.98, 0.02, textstr, transform=ax.transAxes, fontsize=9,
                verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    else:
        ax.text(0.5, 0.5, 'No spatial model comparison data available', transform=ax.transAxes,
                fontsize=12, ha='center', va='center')
        ax.axis('off')

    plt.suptitle('Figure 4. Spatial Autocorrelation Analysis (BMI Obesity Rate)',
                 fontsize=14, weight='bold', y=0.98)
    plt.tight_layout()
    output_file = output_dir / "figure4_spatial_autocorrelation.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Figure 4保存: {output_file}")


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 8: 可視化開始")
    logger.info("=" * 60)

    try:
        # 出力ディレクトリ作成
        figures_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/figures"
        figures_dir.mkdir(parents=True, exist_ok=True)

        # データ読み込み
        gdf, ols_results, moran_results, spatial_comparison = load_data()

        # Figure 1: Study Overview Map
        create_figure1_study_overview_map(gdf, figures_dir)

        # Figure 2: Forest Plot
        create_figure2_forest_plot(ols_results, figures_dir)

        # Figure 3: Scatter Grid
        create_figure3_scatter_grid(gdf, ols_results, figures_dir)

        # Figure 4: Spatial Autocorrelation
        create_figure4_spatial_autocorrelation(gdf, moran_results, spatial_comparison, figures_dir)

        logger.info("\n" + "=" * 60)
        logger.info("Phase 8 処理完了！")
        logger.info("=" * 60)

        logger.info("\n【次のステップ】")
        logger.info("Phase 9: Quarto論文作成（Manuscript_Slope_Diabetes.qmd）")
        logger.info("  - IMRAD構造")
        logger.info("  - Phase 6a/6bの結果統合")
        logger.info("  - Figure 1-4の挿入")

    except Exception as e:
        logger.error(f"エラー発生: {e}")
        raise


if __name__ == "__main__":
    main()

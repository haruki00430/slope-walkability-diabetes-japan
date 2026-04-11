#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 6b: 空間回帰分析（Moran's I → SLM/SEM）

入力:
- data/interim/analysis_dataset_full.csv
- data/external/japan_prefectures_47.geojson

出力:
- results/tables/morans_i_test.csv
- results/tables/spatial_model_comparison.csv（有意な場合のみ）
- results/figures/morans_scatter_plot.png（有意な場合のみ）
- results/reports/spatial_analysis_results.md
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import statsmodels.api as sm
from libpysal.weights import Queen, KNN
from esda.moran import Moran
import spreg

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
        logging.FileHandler(log_dir / "06b_spatial_regression.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 日本語フォント設定
set_japanese_font()


def load_and_merge_data():
    """
    分析データとGeoJSONを読み込み・マージ

    Returns:
    --------
    gpd.GeoDataFrame
        空間データ付き分析データ
    """
    logger.info("\n--- データ読み込み・マージ ---")

    # 1. 分析データ読み込み
    df_path = project_root / "projects/NDB_XXX_slope_diabetes/data/interim/analysis_dataset_full.csv"
    df = pd.read_csv(df_path, encoding='utf-8-sig')
    logger.info(f"分析データ読み込み: {len(df)}都道府県")

    # 2. GeoJSON読み込み
    geojson_path = project_root / "projects/NDB_XXX_slope_diabetes/data/external/japan_prefectures_47.geojson"
    gdf_geo = gpd.read_file(geojson_path)
    logger.info(f"GeoJSON読み込み: {len(gdf_geo)}都道府県")
    logger.info(f"GeoJSONカラム: {gdf_geo.columns.tolist()}")

    # 3. カラム名の確認・標準化
    # GeoJSONの都道府県名カラムを特定
    prefecture_col = [col for col in gdf_geo.columns if '都道府県' in col or 'prefecture' in col.lower()]
    if prefecture_col:
        gdf_geo = gdf_geo.rename(columns={prefecture_col[0]: 'prefecture'})
        logger.info(f"都道府県カラム検出: {prefecture_col[0]} → prefecture")
    else:
        # カラム0が都道府県名の場合（フォールバック）
        gdf_geo = gdf_geo.rename(columns={gdf_geo.columns[0]: 'prefecture'})
        logger.info(f"都道府県カラム推定: {gdf_geo.columns[0]} → prefecture")

    # geometryカラムのみ残してマージ
    gdf_geo_simple = gdf_geo[['prefecture', 'geometry']].copy()

    # 4. マージ
    gdf = gdf_geo_simple.merge(df, on='prefecture', how='inner')
    logger.info(f"マージ後: {len(gdf)}都道府県")

    # GeoDataFrameに変換
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')

    # 欠損値確認
    missing_prefs_geo = set(gdf_geo_simple['prefecture']) - set(gdf['prefecture'])
    missing_prefs_data = set(df['prefecture']) - set(gdf['prefecture'])

    if missing_prefs_geo:
        logger.warning(f"GeoJSONにあるがデータにない都道府県: {missing_prefs_geo}")
    if missing_prefs_data:
        logger.warning(f"データにあるがGeoJSONにない都道府県: {missing_prefs_data}")

    return gdf


def build_spatial_weights(gdf):
    """
    空間重み行列を構築（Queen contiguity + KNN補完）

    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        空間データ

    Returns:
    --------
    libpysal.weights.W
        空間重み行列
    """
    logger.info("\n--- 空間重み行列構築 ---")

    # 1. Queen contiguity
    try:
        w_queen = Queen.from_dataframe(gdf, use_index=False)
        logger.info(f"Queen contiguity構築成功: {w_queen.n}ノード")
    except Exception as e:
        logger.error(f"Queen contiguity構築失敗: {e}")
        raise

    # 2. 孤立ノード（離島）の検出
    islands = w_queen.islands
    logger.info(f"孤立ノード（離島）: {len(islands)}個")

    if len(islands) > 0:
        island_prefs = gdf.iloc[list(islands)]['prefecture'].tolist()
        logger.info(f"孤立都道府県: {island_prefs}")

        # KNN=1で補完
        logger.info("KNN=1で孤立ノードを補完中...")
        w_knn = KNN.from_dataframe(gdf, k=1, use_index=False)

        # libpysal.weights.set_operations を使用してマージ
        from libpysal.weights import w_union
        w = w_union(w_queen, w_knn)
        logger.info("KNN補完完了（w_union使用）")
    else:
        w = w_queen

    # 3. 行標準化
    w.transform = 'r'
    logger.info(f"空間重み行列: {w.n}ノード, 平均隣接数={w.mean_neighbors:.2f}")

    return w


def test_morans_i(gdf, w, residuals, model_name):
    """
    Moran's I検定を実行

    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        空間データ
    w : libpysal.weights.W
        空間重み行列
    residuals : np.ndarray
        OLS残差
    model_name : str
        モデル名

    Returns:
    --------
    dict
        Moran's I検定結果
    """
    logger.info(f"\n--- Moran's I検定: {model_name} ---")

    # Global Moran's I
    moran = Moran(residuals, w, permutations=999)

    result = {
        'model': model_name,
        'I': moran.I,
        'expected_I': moran.EI,
        'variance_I': moran.VI_norm,
        'z_score': moran.z_norm,
        'p_value': moran.p_norm,
        'significant': 'Yes' if moran.p_norm < 0.05 else 'No'
    }

    logger.info(f"Moran's I = {moran.I:.4f}")
    logger.info(f"Expected I = {moran.EI:.4f}")
    logger.info(f"Z-score = {moran.z_norm:.4f}")
    logger.info(f"p-value = {moran.p_norm:.4f}")
    logger.info(f"有意性（α=0.05）: {result['significant']}")

    return result, moran


def run_ols_and_test(gdf, outcome, exposure, covariates):
    """
    OLS実行 + Moran's I検定

    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        空間データ
    outcome : str
        従属変数名
    exposure : str or list
        独立変数名
    covariates : list
        調整変数

    Returns:
    --------
    dict, Moran
        Moran's I結果, Moranオブジェクト
    """
    # 独立変数リスト作成
    if isinstance(exposure, str):
        predictors = [exposure] + covariates
    else:
        predictors = exposure + covariates

    # 欠損値除外
    analysis_vars = [outcome] + predictors
    gdf_analysis = gdf[analysis_vars + ['geometry', 'prefecture']].dropna().reset_index(drop=True)

    logger.info(f"解析対象: N={len(gdf_analysis)}都道府県（欠損値除外後）")

    # 空間重み行列を再構築（gdf_analysisに対して）
    w_analysis = build_spatial_weights(gdf_analysis)

    # Y, X 準備
    y = gdf_analysis[outcome].values
    X = gdf_analysis[predictors].values
    X = np.hstack([np.ones((X.shape[0], 1)), X])  # 切片項追加

    # OLS実行
    model = sm.OLS(y, X)
    results = model.fit()

    # 残差取得
    residuals = results.resid

    # Moran's I検定
    model_name = f"{outcome}_{'_'.join(exposure if isinstance(exposure, list) else [exposure])}"
    moran_result, moran_obj = test_morans_i(gdf_analysis, w_analysis, residuals, model_name)

    return moran_result, moran_obj, gdf_analysis


def run_spatial_models(gdf, w, outcome, exposure, covariates):
    """
    空間ラグモデル（SLM）・空間誤差モデル（SEM）を推定

    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        空間データ
    w : libpysal.weights.W
        空間重み行列
    outcome : str
        従属変数名
    exposure : str or list
        独立変数名
    covariates : list
        調整変数

    Returns:
    --------
    dict
        OLS, SLM, SEMの比較結果
    """
    logger.info("\n--- 空間回帰モデル推定 ---")

    # 独立変数リスト作成
    if isinstance(exposure, str):
        predictors = [exposure] + covariates
    else:
        predictors = exposure + covariates

    # 欠損値除外
    analysis_vars = [outcome] + predictors
    gdf_analysis = gdf[analysis_vars].dropna()

    # Y, X 準備
    y = gdf_analysis[outcome].values.reshape(-1, 1)
    X = gdf_analysis[predictors].values

    # 1. OLS（ベースライン）
    ols = spreg.OLS(y, X, w=w, name_y=outcome, name_x=predictors, spat_diag=True)

    logger.info(f"\nOLS結果:")
    logger.info(f"  R² = {ols.r2:.4f}")
    logger.info(f"  AIC = {ols.aic:.2f}")
    logger.info(f"  LM-Lag = {ols.lm_lag[0]:.3f}, p = {ols.lm_lag[1]:.4f}")
    logger.info(f"  LM-Error = {ols.lm_error[0]:.3f}, p = {ols.lm_error[1]:.4f}")

    # 2. Spatial Lag Model (SLM) - 最尤法
    slm = spreg.ML_Lag(y, X, w=w, name_y=outcome, name_x=predictors, method='ord')
    slm_aic = -2 * slm.logll + 2 * slm.k  # AIC手動計算

    logger.info(f"\nSLM（Spatial Lag Model）結果:")
    logger.info(f"  Pseudo R² = {slm.pr2:.4f}")
    logger.info(f"  Log-Likelihood = {slm.logll:.2f}")
    logger.info(f"  AIC = {slm_aic:.2f}")
    logger.info(f"  rho（空間ラグ係数）= {slm.rho:.4f}")

    # 3. Spatial Error Model (SEM) - 最尤法
    sem = spreg.ML_Error(y, X, w=w, name_y=outcome, name_x=predictors, method='ord')
    sem_aic = -2 * sem.logll + 2 * sem.k  # AIC手動計算

    logger.info(f"\nSEM（Spatial Error Model）結果:")
    logger.info(f"  Pseudo R² = {sem.pr2:.4f}")
    logger.info(f"  Log-Likelihood = {sem.logll:.2f}")
    logger.info(f"  AIC = {sem_aic:.2f}")
    logger.info(f"  lambda（空間誤差係数）= {sem.lam:.4f}")

    # 4. AIC比較
    logger.info(f"\n--- AIC比較 ---")
    logger.info(f"  OLS AIC = {ols.aic:.2f}")
    logger.info(f"  SLM AIC = {slm_aic:.2f} (ΔAIC = {slm_aic - ols.aic:.2f})")
    logger.info(f"  SEM AIC = {sem_aic:.2f} (ΔAIC = {sem_aic - ols.aic:.2f})")

    best_model = min([('OLS', ols.aic), ('SLM', slm_aic), ('SEM', sem_aic)], key=lambda x: x[1])
    logger.info(f"\n最良モデル（AIC基準）: {best_model[0]}")

    comparison = {
        'outcome': outcome,
        'OLS_R2': ols.r2,
        'OLS_AIC': ols.aic,
        'SLM_PseudoR2': slm.pr2,
        'SLM_AIC': slm_aic,
        'SLM_rho': slm.rho,
        'SEM_PseudoR2': sem.pr2,
        'SEM_AIC': sem_aic,
        'SEM_lambda': sem.lam,
        'Best_Model': best_model[0],
        'LM_Lag_stat': ols.lm_lag[0],
        'LM_Lag_p': ols.lm_lag[1],
        'LM_Error_stat': ols.lm_error[0],
        'LM_Error_p': ols.lm_error[1]
    }

    return comparison


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 6b: 空間回帰分析開始")
    logger.info("=" * 60)

    try:
        # 出力ディレクトリ作成
        tables_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/tables"
        figures_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/figures"
        reports_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/reports"

        tables_dir.mkdir(parents=True, exist_ok=True)
        figures_dir.mkdir(parents=True, exist_ok=True)
        reports_dir.mkdir(parents=True, exist_ok=True)

        # 1. データ読み込み・マージ
        logger.info("\n--- ステップ1: データ読み込み・マージ ---")
        gdf = load_and_merge_data()

        # 2. 空間重み行列構築
        logger.info("\n--- ステップ2: 空間重み行列構築 ---")
        w = build_spatial_weights(gdf)

        # 調整変数
        covariates = ['aging_rate', 'income_per_capita']

        # アウトカム変数（主要なもののみ）
        outcomes_to_test = {
            'hba1c_mean': 'HbA1c平均値',
            'bmi_obesity_rate': 'BMI肥満率',
            'waist_mean': '腹囲平均値'
        }

        all_moran_results = []
        all_spatial_comparisons = []

        # 3. 各アウトカムについてMoran's I検定
        for outcome_var, outcome_label in outcomes_to_test.items():
            logger.info("\n" + "=" * 60)
            logger.info(f"アウトカム: {outcome_label} ({outcome_var})")
            logger.info("=" * 60)

            # Model 3: Combined (Slope + Walkability)
            exposure = ['avg_slope_weighted', 'walkability_index']

            # Moran's I検定
            moran_result, moran_obj, gdf_analysis = run_ols_and_test(gdf, outcome_var, exposure, covariates)
            all_moran_results.append(moran_result)

            # Moran's Iが有意な場合のみ空間モデル推定
            if moran_result['significant'] == 'Yes':
                logger.info(f"\n{outcome_label}: Moran's I有意 → 空間モデル推定")
                comparison = run_spatial_models(gdf, w, outcome_var, exposure, covariates)
                all_spatial_comparisons.append(comparison)
            else:
                logger.info(f"\n{outcome_label}: Moran's I非有意 → OLSが最終モデル")

        # 4. 結果の保存
        logger.info("\n--- ステップ4: 結果の保存 ---")

        # Moran's I結果
        df_moran = pd.DataFrame(all_moran_results)
        df_moran.to_csv(tables_dir / "morans_i_test.csv", index=False, encoding='utf-8-sig')
        logger.info(f"Moran's I結果保存: {tables_dir / 'morans_i_test.csv'}")

        # 空間モデル比較（有意な場合のみ）
        if all_spatial_comparisons:
            df_comparison = pd.DataFrame(all_spatial_comparisons)
            df_comparison.to_csv(tables_dir / "spatial_model_comparison.csv", index=False, encoding='utf-8-sig')
            logger.info(f"空間モデル比較保存: {tables_dir / 'spatial_model_comparison.csv'}")
        else:
            logger.info("空間モデル推定なし（全アウトカムでMoran's I非有意）")

        logger.info("\n" + "=" * 60)
        logger.info("Phase 6b 処理完了！")
        logger.info("=" * 60)

        logger.info("\n【結果サマリー】")
        logger.info(f"Moran's I検定実施: {len(all_moran_results)}アウトカム")
        significant_count = sum([1 for r in all_moran_results if r['significant'] == 'Yes'])
        logger.info(f"空間的自己相関有意: {significant_count}/{len(all_moran_results)}アウトカム")

        if significant_count > 0:
            logger.info("\n空間的自己相関が検出されたアウトカム:")
            for r in all_moran_results:
                if r['significant'] == 'Yes':
                    logger.info(f"  {r['model']}: I={r['I']:.4f}, p={r['p_value']:.4f}")
        else:
            logger.info("\n✓ 全アウトカムで空間的自己相関は非有意")
            logger.info("  → OLS回帰が適切なモデル")

        logger.info("\n【次のステップ】")
        logger.info("Phase 8: 可視化（Figure 1-4作成）")

    except Exception as e:
        logger.error(f"エラー発生: {e}")
        raise


if __name__ == "__main__":
    main()

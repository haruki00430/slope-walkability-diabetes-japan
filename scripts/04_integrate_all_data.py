#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 4: Integrate All Datasets into Master Analysis File
       / 全データ統合（解析用マスターデータセット作成）

Merge all intermediate datasets from Phases 1–3 into a single analysis-ready
CSV. Two versions are produced: the full 47-prefecture dataset used for
walkability analyses, and a slope-complete subset (N=25) where terrain data
are available for all prefectures.
Phase 1〜3の全中間データを結合して解析用マスターデータセットを作成する。
全47都道府県版（ウォーカビリティ解析用）と傾斜度データが揃っている
都道府県のみのサブセット（N=25）の2種類を出力する。

Input / 入力:
    data/interim/examination_outcomes.csv      — HbA1c, BMI, waist, triglycerides
    data/interim/questionnaire_exercise.csv    — Exercise habits (Q3–Q4)
    data/interim/terrain_data_47prefs.csv      — Topographic slope / 地形傾斜度
    data/interim/population_walkability.csv    — Population density, DID ratio, walkability
    data/interim/ses_variables.csv             — Income, unemployment, education

Output / 出力:
    data/interim/analysis_dataset_full.csv
        Master analysis dataset, all 47 prefectures, all variables
        解析用マスターデータ（N=47都道府県、全変数）
    data/interim/analysis_dataset_slope_complete.csv
        Subset with complete topographic slope data (N=25)
        傾斜度データが揃っている都道府県のみ（N=25）
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

# プロジェクトルート（NDB_Research_Hub）
project_root = Path(__file__).resolve().parents[3]

# ロガー設定
log_dir = project_root / "projects/NDB_XXX_slope_diabetes/results/logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "04_integrate_all_data.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_all_data():
    """全データファイルを読み込み"""
    interim_dir = project_root / "projects/NDB_XXX_slope_diabetes/data/interim"

    # 1. 検査データ
    df_exam = pd.read_csv(interim_dir / "examination_outcomes.csv", encoding='utf-8-sig')
    logger.info(f"検査データ: {len(df_exam)}都道府県, カラム: {df_exam.columns.tolist()}")

    # 2. 質問票データ
    df_quest = pd.read_csv(interim_dir / "questionnaire_exercise.csv", encoding='utf-8-sig')
    logger.info(f"質問票データ: {len(df_quest)}都道府県, カラム: {df_quest.columns.tolist()}")

    # 3. 地形データ
    df_terrain = pd.read_csv(interim_dir / "terrain_data_47prefs.csv", encoding='utf-8-sig')
    logger.info(f"地形データ: {len(df_terrain)}都道府県, カラム: {df_terrain.columns.tolist()}")

    # 4. 人口密度・Walkability
    df_pop = pd.read_csv(interim_dir / "population_walkability.csv", encoding='utf-8-sig')
    logger.info(f"人口密度・Walkability: {len(df_pop)}都道府県, カラム: {df_pop.columns.tolist()}")

    # 5. 社会経済変数
    df_ses = pd.read_csv(interim_dir / "ses_variables.csv", encoding='utf-8-sig')
    logger.info(f"社会経済変数: {len(df_ses)}都道府県, カラム: {df_ses.columns.tolist()}")

    return df_exam, df_quest, df_terrain, df_pop, df_ses


def merge_datasets(df_exam, df_quest, df_terrain, df_pop, df_ses):
    """
    全データセットを統合

    Parameters:
    -----------
    df_exam : pd.DataFrame
        検査データ
    df_quest : pd.DataFrame
        質問票データ
    df_terrain : pd.DataFrame
        地形データ
    df_pop : pd.DataFrame
        人口密度・Walkability
    df_ses : pd.DataFrame
        社会経済変数

    Returns:
    --------
    pd.DataFrame
        統合データ（N=47）
    """
    logger.info("\n--- データ統合開始 ---")

    # ベースは検査データ（N=47）
    df = df_exam.copy()
    logger.info(f"ベースデータ: {len(df)}都道府県")

    # 1. 質問票データをマージ
    df = df.merge(df_quest, on='prefecture', how='left')
    logger.info(f"質問票マージ後: {len(df)}都道府県")

    # 2. 地形データをマージ（slope有りはN=25のみ）
    # pref_code カラムは不要なので除外
    df_terrain_subset = df_terrain[['prefecture', 'avg_slope_weighted', 'slope_data_available']].copy()
    df = df.merge(df_terrain_subset, on='prefecture', how='left')
    logger.info(f"地形データマージ後: {len(df)}都道府県")
    logger.info(f"slope有りデータ: {df['slope_data_available'].sum()}都道府県")

    # 3. 人口密度・Walkabilityをマージ
    # total_pop, elderly_pop, aging_rate, area は重複する可能性があるので、
    # population_walkability.csv のデータを優先
    df = df.merge(df_pop, on='prefecture', how='left', suffixes=('_old', ''))

    # 重複カラムを削除（_old を削除）
    df = df.loc[:, ~df.columns.str.endswith('_old')]

    logger.info(f"人口密度・Walkabilityマージ後: {len(df)}都道府県")

    # 4. 社会経済変数をマージ
    df = df.merge(df_ses, on='prefecture', how='left')
    logger.info(f"社会経済変数マージ後: {len(df)}都道府県")

    # カラム順序を整理
    columns_ordered = [
        'prefecture',
        # 健康アウトカム
        'hba1c_mean',
        'bmi_obesity_rate',
        'waist_mean',
        'triglycerides_mean',
        # 運動習慣
        'Q3_rate',
        'Q4_rate',
        'exercise_habit_rate',
        # 地形
        'avg_slope_weighted',
        'slope_data_available',
        # 人口・都市化
        'total_pop',
        'elderly_pop',
        'aging_rate',
        'area',
        'pop_density',
        'did_population',
        'did_ratio',
        'walkability_index',
        'walkability_index_scaled',
        # 社会経済
        'income_per_capita',
        'unemployment_rate',
        'college_graduate_rate'
    ]

    df = df[columns_ordered]

    logger.info(f"統合完了: {len(df)}都道府県 × {len(df.columns)}変数")

    return df


def create_slope_complete_dataset(df_full):
    """
    slope有りデータのみを抽出（N=25）

    Parameters:
    -----------
    df_full : pd.DataFrame
        全データ（N=47）

    Returns:
    --------
    pd.DataFrame
        slope有りデータ（N=25）
    """
    df_slope = df_full[df_full['slope_data_available'] == 1.0].copy()
    logger.info(f"slope有りデータ抽出: {len(df_slope)}都道府県")

    # slope_data_available カラムは不要（全て1.0のため）
    df_slope = df_slope.drop(columns=['slope_data_available'])

    return df_slope


def validate_dataset(df, dataset_name="Dataset"):
    """
    データセットの妥当性チェック

    Parameters:
    -----------
    df : pd.DataFrame
        検証対象データ
    dataset_name : str
        データセット名
    """
    logger.info(f"\n--- {dataset_name} 妥当性チェック ---")

    # 1. 欠損値確認
    missing_count = df.isna().sum()
    missing_cols = missing_count[missing_count > 0]

    if len(missing_cols) > 0:
        logger.info(f"欠損値を含むカラム:")
        for col, count in missing_cols.items():
            logger.info(f"  {col}: {count}件 ({count/len(df)*100:.1f}%)")

            # 欠損都道府県を表示（3件まで）
            missing_prefs = df[df[col].isna()]['prefecture'].tolist()[:3]
            if missing_prefs:
                logger.info(f"    例: {', '.join(missing_prefs)}")
    else:
        logger.info("欠損値なし")

    # 2. 重複確認
    duplicates = df.duplicated(subset=['prefecture']).sum()
    assert duplicates == 0, f"都道府県の重複あり: {duplicates}件"
    logger.info(f"✓ 都道府県重複なし")

    # 3. データ型確認
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    logger.info(f"✓ 数値型カラム: {len(numeric_cols)}個")

    # 4. 統計サマリー
    logger.info(f"\n統計サマリー（主要変数のみ）:")
    key_vars = ['hba1c_mean', 'bmi_obesity_rate', 'avg_slope_weighted',
                'walkability_index', 'income_per_capita', 'unemployment_rate']

    for var in key_vars:
        if var in df.columns:
            mean_val = df[var].mean()
            std_val = df[var].std()
            min_val = df[var].min()
            max_val = df[var].max()
            missing_val = df[var].isna().sum()

            logger.info(f"  {var}:")
            logger.info(f"    平均={mean_val:.2f}, SD={std_val:.2f}, 範囲={min_val:.2f}-{max_val:.2f}, 欠損={missing_val}")


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 4: データ統合開始")
    logger.info("=" * 60)

    try:
        # 1. 全データ読み込み
        logger.info("\n--- ステップ1: 全データ読み込み ---")
        df_exam, df_quest, df_terrain, df_pop, df_ses = load_all_data()

        # 2. データ統合
        logger.info("\n--- ステップ2: データ統合 ---")
        df_full = merge_datasets(df_exam, df_quest, df_terrain, df_pop, df_ses)

        # 3. slope有りデータ抽出
        logger.info("\n--- ステップ3: slope有りデータ抽出 ---")
        df_slope = create_slope_complete_dataset(df_full)

        # 4. データ検証
        validate_dataset(df_full, "Full Dataset (N=47)")
        validate_dataset(df_slope, "Slope Complete Dataset (N=25)")

        # 5. データ保存
        logger.info("\n--- ステップ5: データ保存 ---")
        interim_dir = project_root / "projects/NDB_XXX_slope_diabetes/data/interim"

        # Full dataset (N=47)
        output_full = interim_dir / "analysis_dataset_full.csv"
        df_full.to_csv(output_full, index=False, encoding='utf-8-sig')
        logger.info(f"Full dataset保存: {output_full}")
        logger.info(f"  {len(df_full)}都道府県 × {len(df_full.columns)}変数")

        # Slope complete dataset (N=25)
        output_slope = interim_dir / "analysis_dataset_slope_complete.csv"
        df_slope.to_csv(output_slope, index=False, encoding='utf-8-sig')
        logger.info(f"Slope complete dataset保存: {output_slope}")
        logger.info(f"  {len(df_slope)}都道府県 × {len(df_slope.columns)}変数")

        # 6. サンプルデータ表示
        logger.info("\n--- ステップ6: サンプルデータ表示 ---")
        logger.info(f"\nFull dataset (先頭3都道府県):")
        logger.info(df_full.head(3).to_string())

        logger.info(f"\nSlope complete dataset (先頭3都道府県):")
        logger.info(df_slope.head(3).to_string())

        logger.info("\n" + "=" * 60)
        logger.info("Phase 4 処理完了！")
        logger.info("=" * 60)

        # 7. 次のステップ案内
        logger.info("\n【次のステップ】")
        logger.info("Phase 5: 探索的データ解析（EDA・相関分析）")
        logger.info("  - analysis_dataset_full.csv を使用")
        logger.info("  - 相関マトリックス、散布図、分布確認")
        logger.info("  - 多重共線性チェック（VIF）")

    except Exception as e:
        logger.error(f"エラー発生: {e}")
        raise


if __name__ == "__main__":
    main()

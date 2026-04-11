#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 3b: 社会経済変数取得（既存データから取得）

入力:
- projects/NDB_XXX_greenspace_mental_health/data/interim/socioeconomic_data.csv

出力:
- data/interim/ses_variables.csv
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
        logging.FileHandler(log_dir / "03b_acquire_ses_variables.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_socioeconomic_data() -> pd.DataFrame:
    """既存プロジェクトから社会経済データを読み込み"""
    file_path = project_root / "projects/NDB_XXX_greenspace_mental_health/data/interim/socioeconomic_data.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

    df = pd.read_csv(file_path, encoding='utf-8-sig')
    logger.info(f"社会経済データ読み込み: {len(df)}都道府県")
    logger.info(f"カラム: {df.columns.tolist()}")

    return df


def process_ses_variables(df: pd.DataFrame) -> pd.DataFrame:
    """
    必要な変数を抽出・標準化

    Parameters:
    -----------
    df : pd.DataFrame
        元の社会経済データ

    Returns:
    --------
    pd.DataFrame
        処理済みデータ（prefecture, income_per_capita, unemployment_rate, college_graduate_rate）
    """
    # 必要なカラムを抽出
    df_processed = df[['prefecture_name', 'income_per_capita', 'unemployment_rate', 'university_grad_rate']].copy()

    # カラム名を標準化
    df_processed.columns = ['prefecture', 'income_per_capita', 'unemployment_rate', 'college_graduate_rate']

    # 数値型に変換（念のため）
    for col in ['income_per_capita', 'unemployment_rate', 'college_graduate_rate']:
        df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')

    logger.info(f"処理後データ数: {len(df_processed)}都道府県")
    logger.info(f"処理後カラム: {df_processed.columns.tolist()}")

    # 欠損値確認
    missing_count = df_processed.isna().sum()
    if missing_count.sum() > 0:
        logger.warning(f"欠損値:\n{missing_count[missing_count > 0]}")

    return df_processed


def validate_data(df: pd.DataFrame):
    """データの妥当性チェック"""
    logger.info("\n--- データ妥当性チェック ---")

    # 1. 都道府県数チェック
    assert len(df) == 47, f"都道府県数が47ではありません: {len(df)}"
    logger.info(f"✓ 都道府県数: {len(df)}")

    # 2. 所得範囲チェック（1,000〜5,000千円）
    income_min, income_max = df['income_per_capita'].min(), df['income_per_capita'].max()
    assert 1000 <= income_min <= 5000, f"所得最小値が範囲外: {income_min}"
    assert 1000 <= income_max <= 5000, f"所得最大値が範囲外: {income_max}"
    logger.info(f"✓ 所得範囲: {income_min:.2f} - {income_max:.2f}千円")

    # 3. 失業率範囲チェック（1〜10%）
    unemp_min, unemp_max = df['unemployment_rate'].min(), df['unemployment_rate'].max()
    assert 1 <= unemp_min <= 10, f"失業率最小値が範囲外: {unemp_min}"
    assert 1 <= unemp_max <= 10, f"失業率最大値が範囲外: {unemp_max}"
    logger.info(f"✓ 失業率範囲: {unemp_min:.2f}% - {unemp_max:.2f}%")

    # 4. 教育水準範囲チェック（30〜80%）
    edu_min, edu_max = df['college_graduate_rate'].min(), df['college_graduate_rate'].max()
    assert 30 <= edu_min <= 80, f"教育水準最小値が範囲外: {edu_min}"
    assert 30 <= edu_max <= 80, f"教育水準最大値が範囲外: {edu_max}"
    logger.info(f"✓ 教育水準範囲: {edu_min:.2f}% - {edu_max:.2f}%")

    logger.info("✓ 全検証クリア")


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 3b: 社会経済変数取得開始")
    logger.info("=" * 60)

    try:
        # 1. データ読み込み
        logger.info("\n--- ステップ1: データ読み込み ---")
        df = load_socioeconomic_data()

        # 2. データ処理
        logger.info("\n--- ステップ2: データ処理 ---")
        df_ses = process_ses_variables(df)

        # 3. データ検証
        logger.info("\n--- ステップ3: データ検証 ---")
        validate_data(df_ses)

        # 4. データ保存
        logger.info("\n--- ステップ4: データ保存 ---")
        output_file = project_root / "projects/NDB_XXX_slope_diabetes/data/interim/ses_variables.csv"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        df_ses.to_csv(output_file, index=False, encoding='utf-8-sig')

        logger.info(f"出力ファイル: {output_file}")
        logger.info(f"出力データ数: {len(df_ses)}都道府県")
        logger.info(f"出力カラム: {df_ses.columns.tolist()}")

        # 5. 統計サマリー
        logger.info("\n--- ステップ5: 統計サマリー ---")
        logger.info(f"\n{df_ses.describe()}")

        # 6. 上位5都道府県・下位5都道府県
        logger.info("\n--- ステップ6: ランキング ---")

        logger.info("\n【所得（income_per_capita）】")
        logger.info("上位5都道府県:")
        logger.info(df_ses.nlargest(5, 'income_per_capita')[['prefecture', 'income_per_capita']].to_string(index=False))
        logger.info("下位5都道府県:")
        logger.info(df_ses.nsmallest(5, 'income_per_capita')[['prefecture', 'income_per_capita']].to_string(index=False))

        logger.info("\n【失業率（unemployment_rate）】")
        logger.info("上位5都道府県:")
        logger.info(df_ses.nlargest(5, 'unemployment_rate')[['prefecture', 'unemployment_rate']].to_string(index=False))
        logger.info("下位5都道府県:")
        logger.info(df_ses.nsmallest(5, 'unemployment_rate')[['prefecture', 'unemployment_rate']].to_string(index=False))

        logger.info("\n【教育水準（college_graduate_rate）】")
        logger.info("上位5都道府県:")
        logger.info(df_ses.nlargest(5, 'college_graduate_rate')[['prefecture', 'college_graduate_rate']].to_string(index=False))
        logger.info("下位5都道府県:")
        logger.info(df_ses.nsmallest(5, 'college_graduate_rate')[['prefecture', 'college_graduate_rate']].to_string(index=False))

        logger.info("\n" + "=" * 60)
        logger.info("Phase 3b 処理完了！")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"エラー発生: {e}")
        raise


if __name__ == "__main__":
    main()

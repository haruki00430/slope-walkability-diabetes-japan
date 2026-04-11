#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 3a: 人口密度・DID比率取得（Census 2020）

入力:
- data/external/census_2020_population.csv（総人口）
- data/external/census_2020_did_table_1_2.xlsx（DID人口）
- data/external/census_2020_area.csv（面積）

出力:
- data/interim/population_walkability.csv
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
        logging.FileHandler(log_dir / "03a_acquire_population_density.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_population_data() -> pd.DataFrame:
    """総人口データを読み込み"""
    file_path = project_root / "projects/NDB_XXX_slope_diabetes/data/external/census_2020_population.csv"
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    logger.info(f"総人口データ読み込み: {len(df)}都道府県")
    return df


def load_area_data() -> pd.DataFrame:
    """面積データを読み込み"""
    file_path = project_root / "projects/NDB_XXX_slope_diabetes/data/external/census_2020_area.csv"
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    logger.info(f"面積データ読み込み: {len(df)}都道府県")
    return df


def load_did_data() -> pd.DataFrame:
    """
    DID人口データを読み込み（表1-2 Excelファイル）

    Returns:
    --------
    pd.DataFrame : prefecture, did_population
    """
    file_path = project_root / "projects/NDB_XXX_slope_diabetes/data/external/census_2020_did_table_1_2.xlsx"

    logger.info("DIDデータExcel読み込み中...")

    # ヘッダー位置: 行0-4（MultiIndex）、データ: 行5以降
    # header=Noneで生データとして読み込み、手動で処理
    df_raw = pd.read_excel(file_path, sheet_name=0, header=None)

    # データ行は10行目以降（0-indexedで行10）
    # ヘッダー行は行10-14
    # 実際のデータは行15以降
    df = pd.read_excel(file_path, sheet_name=0, header=[10, 11, 12], skiprows=range(0, 10))

    logger.info(f"DID Excel読み込み完了: {df.shape}")
    logger.info(f"カラム数: {len(df.columns)}")

    # カラム名が複雑なMultiIndexなので、位置インデックスで抽出
    # 列0: 地域等級コード
    # 列1: 都道府県名
    # 列3: DID分類
    # 列4: 総人口（DID人口）

    df_simple = df.iloc[:, [0, 1, 3, 4]].copy()
    df_simple.columns = ['region_code', 'prefecture_raw', 'did_class', 'did_population']

    # 都道府県レベル（region_code='a'）かつ DID全域（DID00_全域）を抽出
    df_pref = df_simple[
        (df_simple['region_code'] == 'a') &
        (df_simple['did_class'].str.contains('DID00', na=False))
    ].copy()

    logger.info(f"都道府県レベルデータ: {len(df_pref)}件")

    # 北海道が欠落している場合、市区町村レベルから集計
    if not any(df_pref['prefecture_raw'].str.contains('北海道', na=False)):
        logger.warning("北海道が都道府県レベルデータに含まれていません。市区町村レベルから集計します。")

        # 北海道の市区町村レベルデータを抽出（DID00_全域のみ）
        df_hokkaido_cities = df_simple[
            (df_simple['prefecture_raw'].str.contains('北海道', na=False)) &
            (df_simple['did_class'].str.contains('DID00', na=False))
        ].copy()

        # DID人口を数値型に変換
        df_hokkaido_cities['did_population_num'] = pd.to_numeric(
            df_hokkaido_cities['did_population'], errors='coerce'
        )

        # 北海道全体のDID人口を合計
        hokkaido_did_total = df_hokkaido_cities['did_population_num'].sum()

        logger.info(f"北海道市区町村レベルデータ: {len(df_hokkaido_cities)}件")
        logger.info(f"北海道DID人口合計: {hokkaido_did_total:.0f}人")

        # 北海道行を作成
        hokkaido_row = pd.DataFrame({
            'region_code': ['a'],
            'prefecture_raw': ['01_北海道'],
            'did_class': ['DID00_全域'],
            'did_population': [hokkaido_did_total]
        })

        # 既存データに追加
        df_pref = pd.concat([df_pref, hokkaido_row], ignore_index=True)

    # 都道府県名を標準化（"01_北海道" → "北海道"）
    df_pref['prefecture'] = df_pref['prefecture_raw'].str.replace(r'^\d+_', '', regex=True)

    # DID人口を数値型に変換（"-"はNaNに）
    df_pref['did_population'] = pd.to_numeric(df_pref['did_population'], errors='coerce')

    # 必要カラムのみ抽出
    df_result = df_pref[['prefecture', 'did_population']].copy()

    logger.info(f"DID人口データ抽出完了: {len(df_result)}都道府県")
    logger.info(f"DID人口範囲: {df_result['did_population'].min():.0f} - {df_result['did_population'].max():.0f}人")

    return df_result


def calculate_walkability_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Walkability Indexを計算

    Parameters:
    -----------
    df : pd.DataFrame
        prefecture, total_pop, did_population, area, pop_density

    Returns:
    --------
    pd.DataFrame : walkability_index, did_ratio, pop_density追加
    """
    # DID比率（%）
    df['did_ratio'] = (df['did_population'] / df['total_pop']) * 100

    # Walkability Index（暫定版：人口密度 + DID比率の標準化スコア）
    # より高度な計算は後で実装可能

    # 標準化（Z-score）
    df['pop_density_z'] = (df['pop_density'] - df['pop_density'].mean()) / df['pop_density'].std()
    df['did_ratio_z'] = (df['did_ratio'] - df['did_ratio'].mean()) / df['did_ratio'].std()

    # Walkability Index = (人口密度Z + DID比率Z) / 2
    df['walkability_index'] = (df['pop_density_z'] + df['did_ratio_z']) / 2

    # Min-Max正規化して0-100スケールに（オプション）
    df['walkability_index_scaled'] = (
        (df['walkability_index'] - df['walkability_index'].min()) /
        (df['walkability_index'].max() - df['walkability_index'].min())
    ) * 100

    logger.info("Walkability Index計算完了")
    logger.info(f"DID比率範囲: {df['did_ratio'].min():.2f}% - {df['did_ratio'].max():.2f}%")
    logger.info(f"Walkability Index範囲: {df['walkability_index_scaled'].min():.2f} - {df['walkability_index_scaled'].max():.2f}")

    return df


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 3a: 人口密度・DID比率取得開始")
    logger.info("=" * 60)

    try:
        # 1. 総人口データ読み込み
        logger.info("\n--- ステップ1: 総人口データ読み込み ---")
        df_population = load_population_data()

        # 2. 面積データ読み込み
        logger.info("\n--- ステップ2: 面積データ読み込み ---")
        df_area = load_area_data()

        # 3. DID人口データ読み込み
        logger.info("\n--- ステップ3: DID人口データ読み込み ---")
        df_did = load_did_data()

        # 4. データ統合
        logger.info("\n--- ステップ4: データ統合 ---")
        df = df_population.merge(df_area, on='prefecture', how='inner')
        df = df.merge(df_did, on='prefecture', how='left')

        logger.info(f"統合後データ数: {len(df)}都道府県")

        # 欠損値確認
        missing = df[df['did_population'].isna()]
        if len(missing) > 0:
            logger.warning(f"DID人口が欠損している都道府県: {len(missing)}件")
            logger.warning(f"欠損都道府県: {missing['prefecture'].tolist()}")

        # 5. Walkability Index計算
        logger.info("\n--- ステップ5: Walkability Index計算 ---")
        df = calculate_walkability_index(df)

        # 6. データ保存
        logger.info("\n--- ステップ6: データ保存 ---")
        output_file = project_root / "projects/NDB_XXX_slope_diabetes/data/interim/population_walkability.csv"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 保存するカラムを選択
        columns_to_save = [
            'prefecture',
            'total_pop',
            'elderly_pop',
            'aging_rate',
            'area',
            'pop_density',
            'did_population',
            'did_ratio',
            'walkability_index',
            'walkability_index_scaled'
        ]

        df_output = df[columns_to_save].copy()
        df_output.to_csv(output_file, index=False, encoding='utf-8-sig')

        logger.info(f"出力ファイル: {output_file}")
        logger.info(f"出力データ数: {len(df_output)}都道府県")
        logger.info(f"出力カラム: {df_output.columns.tolist()}")

        # 7. 統計サマリー
        logger.info("\n--- ステップ7: 統計サマリー ---")
        logger.info(f"\n{df_output.describe()}")

        logger.info("\n" + "=" * 60)
        logger.info("Phase 3a 処理完了！")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"エラー発生: {e}")
        raise


if __name__ == "__main__":
    main()

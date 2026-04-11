#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 2b: 地形データ補完（slope_fracture最終データから全47都道府県取得）

入力:
- projects/NDB_XXX_slope_fracture/03_Analysis/data/processed/analysis_dataset_v1.csv
- data/interim/terrain_data_47prefs.csv（既存）
出力: data/interim/terrain_data_47prefs.csv（更新版、47都道府県すべてデータあり）
"""

import pandas as pd
import numpy as np
from pathlib import Path
import yaml
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
        logging.FileHandler(log_dir / "02b_update_terrain_from_slope_fracture.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 2b: 地形データ補完開始（slope_fracture最終データから）")
    logger.info("=" * 60)

    # 1. slope_fractureの最終データセットを読み込み
    slope_fracture_file = project_root / "projects/NDB_XXX_slope_fracture/03_Analysis/data/processed/analysis_dataset_v1.csv"
    if not slope_fracture_file.exists():
        logger.error(f"slope_fractureの最終データセットが見つかりません: {slope_fracture_file}")
        raise FileNotFoundError(f"Slope fracture analysis dataset not found: {slope_fracture_file}")

    df_slope_fracture = pd.read_csv(slope_fracture_file, encoding='utf-8-sig')
    logger.info(f"slope_fracture最終データセット読み込み完了: {df_slope_fracture.shape[0]}都道府県")

    # 2. 必要なカラムを抽出（prefecture, habitable_slope_weighted）
    df_slope = df_slope_fracture[['prefecture', 'habitable_slope_weighted']].copy()
    df_slope = df_slope.rename(columns={'habitable_slope_weighted': 'avg_slope_weighted'})

    # 3. 既存のterrain_data_47prefs.csvを読み込み
    existing_file = project_root / "projects/NDB_XXX_slope_diabetes/data/interim/terrain_data_47prefs.csv"
    df_existing = pd.read_csv(existing_file, encoding='utf-8-sig')
    logger.info(f"既存の地形データ読み込み完了: {df_existing.shape[0]}都道府県")

    # 4. 既存データとマージ（avg_slope_weightedを上書き）
    # pref_codeは維持、avg_slope_weightedのみ更新
    df_updated = df_existing[['pref_code', 'prefecture']].merge(
        df_slope,
        on='prefecture',
        how='left'
    )

    # 5. slope_data_availableを更新（全て1に設定）
    df_updated['slope_data_available'] = 1

    # カラム順序を整理
    df_updated = df_updated[['pref_code', 'prefecture', 'avg_slope_weighted', 'slope_data_available']]

    # 検証
    logger.info("\n--- データ検証 ---")
    logger.info(f"データ形状: {df_updated.shape}")

    # 検証1: 47都道府県確認
    if df_updated.shape[0] != 47:
        logger.error(f"❌ 都道府県数が47ではありません: {df_updated.shape[0]}")
    else:
        logger.info(f"✅ 都道府県数: {df_updated.shape[0]}")

    # 検証2: 全都道府県に地形データあり
    missing_count = df_updated['avg_slope_weighted'].isna().sum()
    if missing_count > 0:
        logger.error(f"❌ {missing_count}都道府県に地形データがありません")
        missing_prefs = df_updated[df_updated['avg_slope_weighted'].isna()]['prefecture'].tolist()
        logger.error(f"欠損都道府県: {', '.join(missing_prefs)}")
    else:
        logger.info(f"✅ 全47都道府県に地形データあり")

    # 検証3: avg_slope_weighted範囲確認
    logger.info(f"✅ 傾斜度範囲: {df_updated['avg_slope_weighted'].min():.2f} - {df_updated['avg_slope_weighted'].max():.2f} 度")

    # 検証4: slope_data_available全て1
    if df_updated['slope_data_available'].sum() != 47:
        logger.warning(f"⚠️ slope_data_availableが全て1ではありません: {df_updated['slope_data_available'].sum()}")
    else:
        logger.info(f"✅ slope_data_available: 全47都道府県で1")

    # 保存（既存ファイルを上書き）
    output_file = existing_file
    df_updated.to_csv(output_file, index=False, encoding="utf-8-sig")

    logger.info(f"\n出力ファイル: {output_file}")
    logger.info(f"\n記述統計:\n{df_updated.describe()}")

    # 変更前後の比較
    logger.info("\n--- 変更前後の比較 ---")
    before_available = df_existing['slope_data_available'].sum()
    after_available = df_updated['slope_data_available'].sum()
    logger.info(f"変更前: {before_available}都道府県にデータあり")
    logger.info(f"変更後: {after_available}都道府県にデータあり")
    logger.info(f"追加: {after_available - before_available}都道府県")

    # 追加された都道府県のリスト
    if before_available < after_available:
        added_prefs = df_updated[df_existing['slope_data_available'] == 0]['prefecture'].tolist()
        logger.info(f"\n追加された都道府県（{len(added_prefs)}）:\n{', '.join(added_prefs)}")

    logger.info("\n" + "=" * 60)
    logger.info("Phase 2b 処理完了")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

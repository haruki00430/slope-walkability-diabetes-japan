#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 2: 地形データ統合（slope_fracture再利用）

入力:
- projects/NDB_XXX_slope_fracture/03_Analysis/data/interim/slope_by_prefecture_final.csv
- data/interim/examination_outcomes.csv（47都道府県リスト）
出力: data/interim/terrain_data_47prefs.csv
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
        logging.FileHandler(log_dir / "02_integrate_terrain_data.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_prefecture_mapping():
    """都道府県名の英語→日本語マッピング辞書を作成"""
    mapping = {
        'Hokkaido': '北海道',
        'Aomori': '青森県',
        'Iwate': '岩手県',
        'Miyagi': '宮城県',
        'Akita': '秋田県',
        'Yamagata': '山形県',
        'Fukushima': '福島県',
        'Ibaraki': '茨城県',
        'Tochigi': '栃木県',
        'Gunma': '群馬県',
        'Saitama': '埼玉県',
        'Chiba': '千葉県',
        'Tokyo': '東京都',
        'Kanagawa': '神奈川県',
        'Niigata': '新潟県',
        'Toyama': '富山県',
        'Ishikawa': '石川県',
        'Fukui': '福井県',
        'Yamanashi': '山梨県',
        'Nagano': '長野県',
        'Gifu': '岐阜県',
        'Shizuoka': '静岡県',
        'Aichi': '愛知県',
        'Mie': '三重県',
        'Shiga': '滋賀県',
        'Kyoto': '京都府',
        'Osaka': '大阪府',
        'Hyogo': '兵庫県',
        'Nara': '奈良県',
        'Wakayama': '和歌山県',
        'Tottori': '鳥取県',
        'Shimane': '島根県',
        'Okayama': '岡山県',
        'Hiroshima': '広島県',
        'Yamaguchi': '山口県',
        'Tokushima': '徳島県',
        'Kagawa': '香川県',
        'Ehime': '愛媛県',
        'Kochi': '高知県',
        'Fukuoka': '福岡県',
        'Saga': '佐賀県',
        'Nagasaki': '長崎県',
        'Kumamoto': '熊本県',
        'Oita': '大分県',
        'Miyazaki': '宮崎県',
        'Kagoshima': '鹿児島県',
        'Okinawa': '沖縄県'
    }
    return mapping


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 2: 地形データ統合開始（slope_fracture再利用）")
    logger.info("=" * 60)

    # 1. 既存の地形データを読み込み
    slope_file = project_root / "projects/NDB_XXX_slope_fracture/03_Analysis/data/interim/slope_by_prefecture_final.csv"
    if not slope_file.exists():
        logger.error(f"地形データファイルが見つかりません: {slope_file}")
        raise FileNotFoundError(f"Slope data file not found: {slope_file}")

    df_slope = pd.read_csv(slope_file)
    logger.info(f"地形データ読み込み完了: {df_slope.shape[0]}都道府県")

    # 2. 都道府県名を英語→日本語に変換
    prefecture_mapping = create_prefecture_mapping()
    df_slope['prefecture_jp'] = df_slope['prefecture'].map(prefecture_mapping)

    # 変換できなかった都道府県をチェック
    unmapped = df_slope[df_slope['prefecture_jp'].isna()]
    if len(unmapped) > 0:
        logger.warning(f"マッピングできなかった都道府県: {unmapped['prefecture'].tolist()}")

    # 3. 47都道府県の標準リストを取得（examination_outcomes.csvから）
    exam_file = project_root / "projects/NDB_XXX_slope_diabetes/data/interim/examination_outcomes.csv"
    if not exam_file.exists():
        logger.error(f"検査データファイルが見つかりません: {exam_file}")
        raise FileNotFoundError(f"Examination data file not found: {exam_file}")

    df_exam = pd.read_csv(exam_file, encoding='utf-8-sig')
    prefectures_47 = df_exam[['prefecture']].copy()
    logger.info(f"47都道府県リスト取得完了: {len(prefectures_47)}都道府県")

    # 4. 地形データを47都道府県にleft join
    df_terrain = prefectures_47.merge(
        df_slope[['prefecture_jp', 'avg_slope_weighted']],
        left_on='prefecture',
        right_on='prefecture_jp',
        how='left'
    )

    # prefecture_jp列を削除（重複）
    df_terrain = df_terrain.drop(columns=['prefecture_jp'])

    # 5. slope_data_available フラグを追加
    df_terrain['slope_data_available'] = df_terrain['avg_slope_weighted'].notna().astype(int)

    # 6. pref_codeを追加（JISコード準拠）
    pref_code_mapping = {
        '北海道': 1, '青森県': 2, '岩手県': 3, '宮城県': 4, '秋田県': 5,
        '山形県': 6, '福島県': 7, '茨城県': 8, '栃木県': 9, '群馬県': 10,
        '埼玉県': 11, '千葉県': 12, '東京都': 13, '神奈川県': 14, '新潟県': 15,
        '富山県': 16, '石川県': 17, '福井県': 18, '山梨県': 19, '長野県': 20,
        '岐阜県': 21, '静岡県': 22, '愛知県': 23, '三重県': 24, '滋賀県': 25,
        '京都府': 26, '大阪府': 27, '兵庫県': 28, '奈良県': 29, '和歌山県': 30,
        '鳥取県': 31, '島根県': 32, '岡山県': 33, '広島県': 34, '山口県': 35,
        '徳島県': 36, '香川県': 37, '愛媛県': 38, '高知県': 39, '福岡県': 40,
        '佐賀県': 41, '長崎県': 42, '熊本県': 43, '大分県': 44, '宮崎県': 45,
        '鹿児島県': 46, '沖縄県': 47
    }
    df_terrain['pref_code'] = df_terrain['prefecture'].map(pref_code_mapping)

    # カラム順序を整理
    df_terrain = df_terrain[['pref_code', 'prefecture', 'avg_slope_weighted', 'slope_data_available']]

    # 検証
    logger.info("\n--- データ検証 ---")
    logger.info(f"データ形状: {df_terrain.shape}")

    # 検証1: 47都道府県確認
    if df_terrain.shape[0] != 47:
        logger.error(f"❌ 都道府県数が47ではありません: {df_terrain.shape[0]}")
    else:
        logger.info(f"✅ 都道府県数: {df_terrain.shape[0]}")

    # 検証2: 地形データ利用可能数
    available_count = df_terrain['slope_data_available'].sum()
    logger.info(f"✅ 地形データ利用可能: {available_count}都道府県")
    logger.info(f"✅ 地形データ欠損: {47 - available_count}都道府県")

    # 検証3: avg_slope_weighted範囲確認
    slope_with_data = df_terrain[df_terrain['slope_data_available'] == 1]['avg_slope_weighted']
    logger.info(f"✅ 傾斜度範囲: {slope_with_data.min():.2f} - {slope_with_data.max():.2f} 度")

    # 保存
    output_path = project_root / "projects/NDB_XXX_slope_diabetes/data/interim"
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "terrain_data_47prefs.csv"
    df_terrain.to_csv(output_file, index=False, encoding="utf-8-sig")

    logger.info(f"\n出力ファイル: {output_file}")
    logger.info(f"\n記述統計:\n{df_terrain.describe()}")

    # 欠損都道府県のリスト表示
    missing_prefs = df_terrain[df_terrain['slope_data_available'] == 0]['prefecture'].tolist()
    logger.info(f"\n地形データ欠損都道府県（22都道府県）:\n{', '.join(missing_prefs)}")

    logger.info("\n" + "=" * 60)
    logger.info("Phase 2 処理完了")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

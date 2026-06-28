#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 1b: Extract NDB Health Checkup Questionnaire Data (Exercise Habits)
        / NDB質問票データ抽出（Q3・Q4運動習慣）

Extract prefecture-level exercise habit response rates from the NDB Open Data
No.10 specific health checkup questionnaire Excel files (Q3: regular exercise,
Q4: walking or equivalent physical activity).
NDB特定健診質問票Excelから都道府県別の運動習慣回答率（Q3・Q4）を抽出する。

Input / 入力:
    NDB Open Data No.10 questionnaire Excel files (Q3, Q4)
    NDB特定健診質問票Excel（Q3, Q4）

Output / 出力:
    data/interim/questionnaire_exercise.csv
        Prefecture-level exercise habit response rates (N=47)
        都道府県別運動習慣回答率（N=47都道府県）
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
        logging.FileHandler(log_dir / "01b_extract_questionnaire_exercise.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    """config.yamlの読み込み"""
    config_path = Path(__file__).parent.parent / "config/config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_questionnaire(file_path, response_target="はい"):
    """
    質問票Excelファイルを読み込み、都道府県別の回答率を算出

    Args:
        file_path: Excelファイルパス
        response_target: 対象回答カテゴリ（デフォルト: "はい"）

    Returns:
        DataFrame: 都道府県別回答率（列: prefecture, response_rate）
    """
    # MultiIndexヘッダーで読み込み
    df = pd.read_excel(file_path, header=[2, 3])

    # 列名を簡素化
    df.columns = [f'{col[0]}_{col[1]}' if col[0] not in ['Unnamed: 0_level_0', 'Unnamed: 1_level_0']
                  else col[1] for col in df.columns]

    df.rename(columns={df.columns[0]: '都道府県', df.columns[1]: '回答'}, inplace=True)

    # ヘッダー行を除外、都道府県名をffill
    df = df[df['回答'].notna()].reset_index(drop=True)
    df['都道府県'] = df['都道府県'].ffill()

    # 「都道府県判別不可」を除外
    df = df[df['都道府県'] != '都道府県判別不可'].reset_index(drop=True)

    # 数値列
    numeric_cols = [col for col in df.columns if col not in ['都道府県', '回答']]

    # 都道府県別の集計
    results = []
    for pref in df['都道府県'].unique():
        df_pref = df[df['都道府県'] == pref]

        # "はい"と"いいえ"の行を抽出
        df_yes = df_pref[df_pref['回答'] == response_target]
        df_no = df_pref[df_pref['回答'] == 'いいえ']

        if len(df_yes) == 0 or len(df_no) == 0:
            logger.warning(f"{pref}: 回答データが不完全（{response_target}={len(df_yes)}, いいえ={len(df_no)}）")
            continue

        # 数値データの合計（'-'をNaNに変換）
        yes_total = df_yes[numeric_cols].replace('-', np.nan).astype(float).sum().sum()
        no_total = df_no[numeric_cols].replace('-', np.nan).astype(float).sum().sum()

        total = yes_total + no_total
        if total == 0:
            logger.warning(f"{pref}: 回答数が0")
            continue

        response_rate = (yes_total / total) * 100

        results.append({
            "prefecture": pref,
            "yes_count": yes_total,
            "total_count": total,
            "response_rate": response_rate
        })

    df_result = pd.DataFrame(results)
    logger.info(f"抽出完了: {len(df_result)}都道府県、平均回答率={df_result['response_rate'].mean():.2f}%")

    return df_result[['prefecture', 'response_rate']]


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 1b: NDB質問票データ抽出開始（Q3・Q4運動習慣）")
    logger.info("=" * 60)

    # Config読み込み
    config = load_config()
    base_path = project_root / config["input_paths"]["questionnaire"]
    output_path = project_root / config["output_paths"]["interim"]
    output_path.mkdir(parents=True, exist_ok=True)

    # Q3（30分×週2回以上運動）
    logger.info("\n--- Q3処理開始（30分×週2回以上運動） ---")
    q3_file = base_path / config["adjustment_variables"]["exercise"]["file_names"]["q3"]
    if not q3_file.exists():
        logger.error(f"ファイルが見つかりません: {q3_file}")
        raise FileNotFoundError(f"Q3ファイルが存在しません: {q3_file}")
    else:
        df_q3 = load_questionnaire(q3_file, response_target="はい")
        df_q3 = df_q3.rename(columns={"response_rate": "Q3_rate"})

    # Q4（1日1時間以上歩行）
    logger.info("\n--- Q4処理開始（1日1時間以上歩行） ---")
    q4_file = base_path / config["adjustment_variables"]["exercise"]["file_names"]["q4"]
    if not q4_file.exists():
        logger.error(f"ファイルが見つかりません: {q4_file}")
        raise FileNotFoundError(f"Q4ファイルが存在しません: {q4_file}")
    else:
        df_q4 = load_questionnaire(q4_file, response_target="はい")
        df_q4 = df_q4.rename(columns={"response_rate": "Q4_rate"})

    # Q3とQ4を統合
    logger.info("\n--- データ統合 ---")
    df_merged = df_q3.merge(df_q4, on="prefecture", how="outer")

    # exercise_habit_rate = (Q3_rate + Q4_rate) / 2
    df_merged['exercise_habit_rate'] = (df_merged['Q3_rate'] + df_merged['Q4_rate']) / 2

    # 欠損値チェック
    missing_count = df_merged.isnull().sum()
    if missing_count.any():
        logger.warning(f"欠損値あり:\n{missing_count[missing_count > 0]}")

    # 検証
    logger.info("\n--- データ検証 ---")
    logger.info(f"データ形状: {df_merged.shape}")

    # 検証1: 47都道府県確認
    if df_merged.shape[0] != 47:
        logger.error(f"❌ 都道府県数が47ではありません: {df_merged.shape[0]}")
    else:
        logger.info(f"✅ 都道府県数: {df_merged.shape[0]}")

    # 検証2: Q3回答率範囲確認（10-40%）
    q3_valid = df_merged['Q3_rate'].between(10, 40).all()
    if not q3_valid:
        logger.warning(f"❌ Q3回答率が範囲外の都道府県があります")
    else:
        logger.info(f"✅ Q3回答率範囲: {df_merged['Q3_rate'].min():.2f} - {df_merged['Q3_rate'].max():.2f}%")

    # 検証3: Q4回答率範囲確認（20-60%）
    q4_valid = df_merged['Q4_rate'].between(20, 60).all()
    if not q4_valid:
        logger.warning(f"❌ Q4回答率が範囲外の都道府県があります")
    else:
        logger.info(f"✅ Q4回答率範囲: {df_merged['Q4_rate'].min():.2f} - {df_merged['Q4_rate'].max():.2f}%")

    # 保存
    output_file = output_path / "questionnaire_exercise.csv"
    df_merged.to_csv(output_file, index=False, encoding="utf-8-sig")

    logger.info(f"\n出力ファイル: {output_file}")
    logger.info(f"\n記述統計:\n{df_merged.describe()}")

    logger.info("\n" + "=" * 60)
    logger.info("Phase 1b 処理完了")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

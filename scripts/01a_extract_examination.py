#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 1a: NDB検査データ抽出（HbA1c、BMI、腹囲、中性脂肪）

入力: NDB特定健診検査Excel（HbA1c、BMI、中性脂肪、腹囲）
出力: examination_outcomes.csv（都道府県別検査指標）
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
        logging.FileHandler(log_dir / "01a_extract_examination.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    """config.yamlの読み込み"""
    config_path = Path(__file__).parent.parent / "config/config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_hba1c(file_path):
    """
    HbA1cカテゴリ別データから都道府県別平均値を算出

    Args:
        file_path: Excelファイルパス

    Returns:
        DataFrame: 都道府県別HbA1c平均値（列: prefecture, hba1c_mean）
    """
    # MultiIndexヘッダーで読み込み
    df = pd.read_excel(file_path, header=[2, 3])

    # 列名を簡素化
    df.columns = [f'{col[0]}_{col[1]}' if col[0] not in ['Unnamed: 0_level_0', 'Unnamed: 1_level_0']
                  else col[1] for col in df.columns]

    df.rename(columns={df.columns[0]: '都道府県', df.columns[1]: 'カテゴリ'}, inplace=True)

    # ヘッダー行を除外、都道府県名をffill
    df = df[df['カテゴリ'].notna()].reset_index(drop=True)
    df['都道府県'] = df['都道府県'].ffill()

    # 「都道府県判別不可」を除外
    df = df[df['都道府県'] != '都道府県判別不可'].reset_index(drop=True)

    # 数値列
    numeric_cols = [col for col in df.columns if col not in ['都道府県', 'カテゴリ']]

    # カテゴリ別の中央値マッピング
    category_midpoints = {
        '8.4以上': 8.5,
        '8.0以上8.4未満': 8.2,
        '6.5以上8.0未満': 7.25,
        '6.0以上6.5未満': 6.25,
        '5.6以上6.0未満': 5.8,
        '5.6未満': 5.3
    }

    # 都道府県別の加重平均計算
    results = []
    for pref in df['都道府県'].unique():
        df_pref = df[df['都道府県'] == pref]

        total_count = 0
        weighted_sum = 0

        for _, row in df_pref.iterrows():
            category = row['カテゴリ']
            if category not in category_midpoints:
                logger.warning(f"{pref}: 未知のカテゴリ '{category}'")
                continue

            midpoint = category_midpoints[category]

            # 性別×年齢階級の合計人数（'-'をNaNに変換）
            count = row[numeric_cols].replace('-', np.nan).astype(float).sum()

            if not np.isnan(count):
                total_count += count
                weighted_sum += midpoint * count

        if total_count == 0:
            logger.warning(f"{pref}: HbA1cデータなし")
            continue

        hba1c_mean = weighted_sum / total_count

        results.append({
            "prefecture": pref,
            "hba1c_mean": hba1c_mean,
            "total_count": total_count
        })

    df_result = pd.DataFrame(results)
    logger.info(f"HbA1c抽出完了: {len(df_result)}都道府県、平均={df_result['hba1c_mean'].mean():.2f}%")

    return df_result[['prefecture', 'hba1c_mean']]


def load_bmi_obesity(file_path, threshold=25):
    """
    BMIカテゴリ別データから都道府県別肥満者割合を算出

    Args:
        file_path: Excelファイルパス
        threshold: 肥満の閾値（デフォルト: 25）

    Returns:
        DataFrame: 都道府県別肥満者割合（列: prefecture, bmi_obesity_rate）
    """
    # MultiIndexヘッダーで読み込み
    df = pd.read_excel(file_path, header=[2, 3])

    # 列名を簡素化
    df.columns = [f'{col[0]}_{col[1]}' if col[0] not in ['Unnamed: 0_level_0', 'Unnamed: 1_level_0']
                  else col[1] for col in df.columns]

    df.rename(columns={df.columns[0]: '都道府県', df.columns[1]: 'カテゴリ'}, inplace=True)

    # ヘッダー行を除外、都道府県名をffill
    df = df[df['カテゴリ'].notna()].reset_index(drop=True)
    df['都道府県'] = df['都道府県'].ffill()

    # 「都道府県判別不可」を除外
    df = df[df['都道府県'] != '都道府県判別不可'].reset_index(drop=True)

    # 数値列
    numeric_cols = [col for col in df.columns if col not in ['都道府県', 'カテゴリ']]

    # 都道府県別の肥満者割合計算
    results = []
    for pref in df['都道府県'].unique():
        df_pref = df[df['都道府県'] == pref]

        total_count = 0
        obese_count = 0

        for _, row in df_pref.iterrows():
            category = row['カテゴリ']
            count = row[numeric_cols].replace('-', np.nan).astype(float).sum()

            if not np.isnan(count):
                total_count += count

                # カテゴリ文字列からBMI値を抽出（例: "25以上30未満"）
                if '以上' in category:
                    # 下限値を抽出
                    lower_bound = float(category.split('以上')[0])
                    if lower_bound >= threshold:
                        obese_count += count

        if total_count == 0:
            logger.warning(f"{pref}: BMIデータなし")
            continue

        obesity_rate = (obese_count / total_count) * 100

        results.append({
            "prefecture": pref,
            "bmi_obesity_rate": obesity_rate,
            "obese_count": obese_count,
            "total_count": total_count
        })

    df_result = pd.DataFrame(results)
    logger.info(f"BMI肥満者割合抽出完了: {len(df_result)}都道府県、平均={df_result['bmi_obesity_rate'].mean():.2f}%")

    return df_result[['prefecture', 'bmi_obesity_rate']]


def load_continuous_mean(file_path, var_name):
    """
    連続値カテゴリ別データから都道府県別平均値を算出（中性脂肪、腹囲など）

    Args:
        file_path: Excelファイルパス
        var_name: 変数名（ログ用）

    Returns:
        DataFrame: 都道府県別平均値（列: prefecture, {var_name}）
    """
    # MultiIndexヘッダーで読み込み
    df = pd.read_excel(file_path, header=[2, 3])

    # 列名を簡素化
    df.columns = [f'{col[0]}_{col[1]}' if col[0] not in ['Unnamed: 0_level_0', 'Unnamed: 1_level_0']
                  else col[1] for col in df.columns]

    df.rename(columns={df.columns[0]: '都道府県', df.columns[1]: 'カテゴリ'}, inplace=True)

    # ヘッダー行を除外、都道府県名をffill
    df = df[df['カテゴリ'].notna()].reset_index(drop=True)
    df['都道府県'] = df['都道府県'].ffill()

    # 「都道府県判別不可」を除外
    df = df[df['都道府県'] != '都道府県判別不可'].reset_index(drop=True)

    # 数値列
    numeric_cols = [col for col in df.columns if col not in ['都道府県', 'カテゴリ']]

    # カテゴリから中央値を計算する関数
    def get_category_midpoint(category_str):
        """カテゴリ文字列から中央値を算出（例: "100以上120未満" → 110）"""
        try:
            if '以上' in category_str and '未満' in category_str:
                parts = category_str.replace('以上', ',').replace('未満', '').split(',')
                lower = float(parts[0])
                upper = float(parts[1])
                return (lower + upper) / 2
            elif '以上' in category_str:
                # 上限なし（例: "300以上"）→ 下限+50を仮の中央値とする
                lower = float(category_str.replace('以上', ''))
                return lower + 50
            elif '未満' in category_str:
                # 下限なし（例: "50未満"）→ 上限-25を仮の中央値とする
                upper = float(category_str.replace('未満', ''))
                return upper - 25
            else:
                return np.nan
        except:
            return np.nan

    # 都道府県別の加重平均計算
    results = []
    for pref in df['都道府県'].unique():
        df_pref = df[df['都道府県'] == pref]

        total_count = 0
        weighted_sum = 0

        for _, row in df_pref.iterrows():
            category = row['カテゴリ']
            midpoint = get_category_midpoint(category)

            if np.isnan(midpoint):
                logger.warning(f"{pref}: カテゴリ '{category}' の中央値算出不可")
                continue

            count = row[numeric_cols].replace('-', np.nan).astype(float).sum()

            if not np.isnan(count):
                total_count += count
                weighted_sum += midpoint * count

        if total_count == 0:
            logger.warning(f"{pref}: {var_name}データなし")
            continue

        mean_value = weighted_sum / total_count

        results.append({
            "prefecture": pref,
            var_name: mean_value,
            "total_count": total_count
        })

    df_result = pd.DataFrame(results)
    logger.info(f"{var_name}抽出完了: {len(df_result)}都道府県、平均={df_result[var_name].mean():.2f}")

    return df_result[['prefecture', var_name]]


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Phase 1a: NDB検査データ抽出開始")
    logger.info("=" * 60)

    # Config読み込み
    config = load_config()
    base_path = project_root / config["input_paths"]["examination"]
    output_path = project_root / config["output_paths"]["interim"]
    output_path.mkdir(parents=True, exist_ok=True)

    # HbA1c平均値
    logger.info("\n--- HbA1c処理開始 ---")
    hba1c_file = base_path / config["outcome_variables"]["hba1c"]["file_name"]
    if not hba1c_file.exists():
        logger.error(f"ファイルが見つかりません: {hba1c_file}")
        raise FileNotFoundError(f"HbA1cファイルが存在しません: {hba1c_file}")
    else:
        df_hba1c = load_hba1c(hba1c_file)

    # BMI肥満者割合
    logger.info("\n--- BMI処理開始 ---")
    bmi_file = base_path / config["outcome_variables"]["bmi_obesity"]["file_name"]
    if not bmi_file.exists():
        logger.error(f"ファイルが見つかりません: {bmi_file}")
        raise FileNotFoundError(f"BMIファイルが存在しません: {bmi_file}")
    else:
        df_bmi = load_bmi_obesity(bmi_file, threshold=config["outcome_variables"]["bmi_obesity"]["threshold"])

    # 中性脂肪平均値
    logger.info("\n--- 中性脂肪処理開始 ---")
    tg_file = base_path / config["outcome_variables"]["triglycerides"]["file_name"]
    if not tg_file.exists():
        logger.error(f"ファイルが見つかりません: {tg_file}")
        raise FileNotFoundError(f"中性脂肪ファイルが存在しません: {tg_file}")
    else:
        df_tg = load_continuous_mean(tg_file, config["outcome_variables"]["triglycerides"]["variable_name"])

    # 腹囲平均値
    logger.info("\n--- 腹囲処理開始 ---")
    waist_file = base_path / config["outcome_variables"]["waist"]["file_name"]
    if not waist_file.exists():
        logger.error(f"ファイルが見つかりません: {waist_file}")
        raise FileNotFoundError(f"腹囲ファイルが存在しません: {waist_file}")
    else:
        df_waist = load_continuous_mean(waist_file, config["outcome_variables"]["waist"]["variable_name"])

    # 4つの指標を統合
    logger.info("\n--- データ統合 ---")
    df_merged = df_hba1c
    for df in [df_bmi, df_tg, df_waist]:
        df_merged = df_merged.merge(df, on="prefecture", how="outer")

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

    # 検証2: HbA1c範囲確認（5.5-7.0）
    hba1c_valid = df_merged['hba1c_mean'].between(5.5, 7.0).all()
    if not hba1c_valid:
        logger.warning(f"❌ HbA1cが範囲外の都道府県があります")
    else:
        logger.info(f"✅ HbA1c範囲: {df_merged['hba1c_mean'].min():.2f} - {df_merged['hba1c_mean'].max():.2f}%")

    # 検証3: BMI肥満率範囲確認（10-50）
    bmi_valid = df_merged['bmi_obesity_rate'].between(10, 50).all()
    if not bmi_valid:
        logger.warning(f"❌ BMI肥満率が範囲外の都道府県があります")
    else:
        logger.info(f"✅ BMI肥満率範囲: {df_merged['bmi_obesity_rate'].min():.2f} - {df_merged['bmi_obesity_rate'].max():.2f}%")

    # 保存
    output_file = output_path / "examination_outcomes.csv"
    df_merged.to_csv(output_file, index=False, encoding="utf-8-sig")

    logger.info(f"\n出力ファイル: {output_file}")
    logger.info(f"\n記述統計:\n{df_merged.describe()}")

    logger.info("\n" + "=" * 60)
    logger.info("Phase 1a 処理完了")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

# Phase 5: 探索的データ解析レポート

## 1. データ概要

- **N**: 47都道府県
- **変数数**: 22変数
- **欠損データ**: なし（全変数完全データ）

## 2. 記述統計（Table 1）

| Variable                 |   N |             Mean |               SD |       Min |             Max |
|:-------------------------|----:|-----------------:|-----------------:|----------:|----------------:|
| hba1c_mean               |  47 |      5.74        |      0.04        |      5.64 |     5.83        |
| bmi_obesity_rate         |  47 |     30.08        |      2.55        |     26.06 |    39.85        |
| waist_mean               |  47 |     84.2         |      1.64        |     81.48 |    90.76        |
| triglycerides_mean       |  47 |    148.76        |      1.74        |    145.93 |   154.56        |
| Q3_rate                  |  47 |     16.48        |      1.39        |     13.69 |    20.5         |
| Q4_rate                  |  47 |      1.81        |      0.28        |      1.12 |     2.87        |
| exercise_habit_rate      |  47 |      9.14        |      0.73        |      7.79 |    11.27        |
| avg_slope_weighted       |  47 |      8.57        |      3.16        |      1.81 |    15.43        |
| total_pop                |  47 |      2.68396e+06 |      2.79658e+06 | 553407    |     1.40476e+07 |
| elderly_pop              |  47 | 766377           | 688820           | 180371    |     3.19201e+06 |
| aging_rate               |  47 |     30.74        |      3.1         |     22.61 |    36.45        |
| area                     |  47 |   8042.04        |  11694.8         |   1876.78 | 83423.8         |
| pop_density              |  47 |    657           |   1223.13        |     62.63 |  6402.64        |
| did_population           |  47 |      1.87318e+06 |      2.74569e+06 | 171792    |     1.3844e+07  |
| did_ratio                |  47 |     53.85        |     18.65        |     25.6  |    98.55        |
| walkability_index        |  47 |     -0           |      0.93        |     -0.99 |     3.55        |
| walkability_index_scaled |  47 |     21.74        |     20.5         |      0    |   100           |
| income_per_capita        |  47 |   1575.84        |    269.35        |   1272.28 |  2793.71        |
| unemployment_rate        |  47 |      4.77        |      0.51        |      3.62 |     6.29        |
| college_graduate_rate    |  47 |     57.56        |      7.07        |     46.7  |    74.1         |

## 3. 相関分析

### 主要な相関

**アウトカム vs 曝露変数:**
- HbA1c vs Slope: r=0.066
- HbA1c vs Walkability: r=-0.546
- BMI vs Slope: r=-0.401
- BMI vs Walkability: r=-0.132

### 多重共線性チェック（VIF）

| Variable              |       VIF |
|:----------------------|----------:|
| avg_slope_weighted    |  14.8743  |
| walkability_index     |   3.71741 |
| aging_rate            | 233.011   |
| income_per_capita     | 169.425   |
| unemployment_rate     | 108.368   |
| exercise_habit_rate   | 251.871   |
| college_graduate_rate | 216.276   |

**判定**: VIF > 5.0の変数あり（要注意）

## 4. 正規性検定

主要アウトカム変数のShapiro-Wilk検定結果は分布プロットを参照。

## 5. 次のステップ

- **Phase 6a**: OLS回帰分析（Walkability & Slope models）
- **Phase 6b**: 空間回帰分析（Moran's I検定 → SLM/SEM）

## ファイル出力

- 相関ヒートマップ: `results/figures/eda_correlation_heatmap.png`
- 分布プロット: `results/figures/eda_distributions.png`
- 二変量散布図: `results/figures/eda_bivariate_scatter.png`

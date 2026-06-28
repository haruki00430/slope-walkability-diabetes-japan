# Scripts — Execution Guide / 実行手順ガイド

This directory contains all analysis scripts for the slope–walkability–diabetes ecological study.
Run them in the numbered order shown below.

このディレクトリには解析スクリプトが含まれます。以下の番号順に実行してください。

---

## Environment Setup / 環境構築

```bash
# Create virtual environment / 仮想環境の作成
python -m venv .venv

# Activate / 有効化
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install dependencies / 依存パッケージのインストール
pip install -r ../requirements.txt
```

---

## Data Prerequisites / データの前提条件

The following data must be obtained **before** running the scripts.
以下のデータはスクリプト実行前に取得してください。

| Data | Source / 入手先 | Place at / 配置先 |
|------|----------------|------------------|
| NDB Open Data No.10 examination Excel files | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html | `../../../02_Data/raw/NDB_OpenData/No.10/` |
| NDB Open Data No.10 questionnaire Excel files | same as above / 同上 | `../../../02_Data/raw/NDB_OpenData/No.10/` |
| Population Census 2020 CSV / XLSX | https://www.e-stat.go.jp/ | `data/external/` |
| Japan prefecture boundary GeoJSON | Geospatial Information Authority / 国土地理院 | `data/external/japan_prefectures_47.geojson` |

> **Note / 注意:** NDB raw data files are read-only and must **not** be modified.
> NDB生データは読み取り専用です。変更しないでください。

---

## Execution Order / 実行順序

### Phase 1 — Extract NDB Health Checkup Data / NDB特定健診データ抽出

```bash
python 01a_extract_examination.py
python 01b_extract_questionnaire_exercise.py
```

| Script | Input / 入力 | Output / 出力 |
|--------|-------------|--------------|
| `01a_extract_examination.py` | NDB examination Excel (HbA1c, BMI, waist, TG) | `data/interim/examination_outcomes.csv` |
| `01b_extract_questionnaire_exercise.py` | NDB questionnaire Excel (Q3, Q4) | `data/interim/questionnaire_exercise.csv` |

---

### Phase 2 — Integrate Topographic Slope Data / 地形傾斜度データ統合

```bash
python 02_integrate_terrain_data.py
python 02b_update_terrain_from_slope_fracture.py
```

| Script | Input / 入力 | Output / 出力 |
|--------|-------------|--------------|
| `02_integrate_terrain_data.py` | `slope_by_prefecture_final.csv` (NDB_XXX_slope_fracture project) | `data/interim/terrain_data_47prefs.csv` |
| `02b_update_terrain_from_slope_fracture.py` | `analysis_dataset_v1.csv` (slope_fracture) | `data/interim/terrain_data_47prefs.csv` (updated, all 47 prefs) |

---

### Phase 3 — Acquire Walkability Index and Socioeconomic Variables / ウォーカビリティ指数・社会経済変数取得

```bash
python 03a_acquire_population_density.py
python 03b_acquire_ses_variables.py
```

| Script | Input / 入力 | Output / 出力 |
|--------|-------------|--------------|
| `03a_acquire_population_density.py` | Census 2020 CSV/XLSX (population, DID, area) | `data/interim/population_walkability.csv` |
| `03b_acquire_ses_variables.py` | Shared socioeconomic data from greenspace project | `data/interim/ses_variables.csv` |

---

### Phase 4 — Merge All Datasets / 全データ統合

```bash
python 04_integrate_all_data.py
```

| Script | Input / 入力 | Output / 出力 |
|--------|-------------|--------------|
| `04_integrate_all_data.py` | All `data/interim/` CSVs from Phases 1–3 | `data/interim/analysis_dataset_full.csv` (N=47), `data/interim/analysis_dataset_slope_complete.csv` (N=25) |

---

### Phase 5 — Exploratory Data Analysis / 探索的データ解析

```bash
python 05_exploratory_analysis.py
```

| Script | Input / 入力 | Output / 出力 |
|--------|-------------|--------------|
| `05_exploratory_analysis.py` | `analysis_dataset_full.csv` | Correlation heatmap, distribution plots, Table 1, VIF table |

---

### Phase 6 — Statistical Analysis / 統計解析

```bash
python 06a_ols_regression.py
python 06b_spatial_regression.py
```

| Script | Input / 入力 | Output / 出力 |
|--------|-------------|--------------|
| `06a_ols_regression.py` | `analysis_dataset_full.csv` | OLS regression tables (Models 1–3 × 4 outcomes), diagnostics plot |
| `06b_spatial_regression.py` | `analysis_dataset_full.csv`, `japan_prefectures_47.geojson` | Moran's I results, SLM/SEM comparison (if significant), LISA map |

---

### Phase 8 — Generate Manuscript Figures / 論文図作成

```bash
python 08_create_figures.py
```

| Script | Input / 入力 | Output / 出力 |
|--------|-------------|--------------|
| `08_create_figures.py` | `analysis_dataset_full.csv`, GeoJSON, OLS/spatial result tables | `figure1_study_overview_map.png`, `figure2_forest_plot.png`, `figure3_scatter_grid.png`, `figure4_spatial_autocorrelation.png` |

---

## Output Files / 出力ファイル一覧

```
data/interim/
├── examination_outcomes.csv           # Prefecture-level health checkup indicators
├── questionnaire_exercise.csv         # Exercise habit response rates
├── terrain_data_47prefs.csv           # Topographic slope for all 47 prefectures
├── population_walkability.csv         # Walkability index (population density + DID ratio)
├── ses_variables.csv                  # Socioeconomic covariates
├── analysis_dataset_full.csv          # Master dataset (N=47, all variables)
└── analysis_dataset_slope_complete.csv # Subset with complete slope data (N=25)

results/
├── figures/
│   ├── eda_correlation_heatmap.png
│   ├── eda_distributions.png
│   ├── eda_bivariate_scatter.png
│   ├── ols_diagnostics.png
│   ├── figure1_study_overview_map.png
│   ├── figure2_forest_plot.png
│   ├── figure3_scatter_grid.png
│   └── figure4_spatial_autocorrelation.png
├── tables/
│   ├── table1_descriptive_stats.csv
│   ├── correlation_matrix.csv
│   ├── vif_multicollinearity.csv
│   ├── ols_summary_all_outcomes.csv
│   ├── morans_i_test.csv
│   └── spatial_model_comparison.csv
└── reports/
    ├── eda_summary.md
    ├── ols_regression_results.md
    └── spatial_analysis_results.md
```

---

## Notes / 注意事項

- NDB raw data (`02_Data/raw/`) must **not** be modified or committed to Git.  
  NDB生データは変更・コミット禁止。
- All scripts use `config/config.yaml` for parameters (exposures, outcomes, file paths).  
  全スクリプトは `config/config.yaml` で設定を管理しています。
- Random seed is fixed to 42 where applicable.  
  乱数シードは 42 に固定しています。

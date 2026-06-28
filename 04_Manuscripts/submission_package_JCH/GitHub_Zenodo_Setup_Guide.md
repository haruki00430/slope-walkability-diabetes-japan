# GitHub / Zenodo 設定手順書
# slope-walkability-diabetes-japan — JCH 投稿版
# 作成日: 2026-06-28

---

## 1. GitHub リポジトリの現状と方針

### 現在のリポジトリ

- **URL（現状）:** https://github.com/haruki00430/NDB_XXX_slope_diabetes
- **名前（現状）:** `NDB_XXX_slope_diabetes`
- **公開設定:** Private（→ Public に変更要）

### リポジトリ名の変更検討

| 案 | 長所 | 短所 |
|----|------|------|
| **現状維持**（`NDB_XXX_slope_diabetes`） | URLを変えない | 内部的すぎる名前 |
| `slope-walkability-diabetes-japan` ★推奨 | 国際読者に分かりやすい・内容を反映 | URLが変わる |
| `ndb-slope-diabetes-japan` | NDBをアピール | 内容がやや狭い |
| `built-environment-diabetes-japan` | 広い概念で収まりよい | slopeが不明確 |

**推奨:** Zenodo 登録前に `slope-walkability-diabetes-japan` に変更する。  
GitHub はリポジトリ名変更後に自動リダイレクトを提供するため、既存リンクは引き続き機能する。

### リポジトリ名変更手順

1. GitHub → リポジトリ → Settings → General → Repository name
2. `slope-walkability-diabetes-japan` を入力 → Rename

---

## 2. GitHub Public化の手順

### 2-1. リポジトリの整備（必須ファイル）

```
slope-walkability-diabetes-japan/
├── README.md                         ← 必須（英語メイン・日本語セクションあり）
├── LICENSE                           ← 必須（CC-BY 4.0）
├── .gitignore                        ← 必須（NDB データ除外）
├── requirements.txt                  ← 必須（再現性）
├── 03_Analysis/
│   └── scripts/
│       ├── 01_data_preparation.py
│       ├── 02_regression_ols.py
│       ├── 03_spatial_analysis.py
│       ├── 04_visualization.py
│       └── README.md                 ← 実行手順
├── 04_Manuscripts/
│   └── core/manuscript_core.qmd     ← Quarto ソース（データなし）
└── 03_Analysis/results/figures/     ← 生成済み図（Git 管理可）
    ├── figure1_study_overview_map.png
    ├── figure2_forest_plot.png
    ├── figure3_scatter_grid.png
    └── figure4_spatial_autocorrelation.png
```

**絶対に含めてはいけないもの:**
- `02_Data/raw/` 内の NDB Excel ファイル
- `02_Data/interim/` の Parquet / CSV
- `.claude/`, `.cursor/`, `.gemini/`, `.obsidian/`

### 2-2. .gitignore の確認

```gitignore
# NDB 生データ（絶対除外）
02_Data/raw/
02_Data/interim/*.parquet
02_Data/interim/*.csv
02_Data/interim/*.pkl

# 設定フォルダ（除外）
.claude/
.cursor/
.obsidian/
.gemini/

# Python
__pycache__/
*.pyc
.venv/
*.log

# OS
.DS_Store
Thumbs.db
desktop.ini
```

### 2-3. README.md（英語・日本語）

```markdown
# Topographic Slope, Urban Walkability, and Diabetes in Japan

**A Spatial Ecological Study of 47 Japanese Prefectures Using NDB Open Data**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

## Citation

Saito H, Ohira T. Association between Topographic Slope, Urban Walkability, and
Diabetes Management Indicators: An Ecological Study of 47 Japanese Prefectures.
*Journal of Community Health*. [in review] 2026.

## Overview

This study examines the associations between topographic slope, urban walkability, and
four diabetes-related indicators (HbA1c, BMI obesity rate, waist circumference, triglycerides)
across all 47 Japanese prefectures, using data from the National Database of Health Insurance
Claims (NDB) Open Data for fiscal year 2023.

**Key Findings:**
- Urban walkability was consistently protective across all diabetes indicators
- BMI obesity exhibited strong spatial spillover (rho = 0.753, p < 0.001)
- HbA1c showed no spatial autocorrelation, suggesting local management factors dominate

## Data Sources

- **NDB Open Data No.10 (FY2023):** https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html
- **Digital Elevation Model (DEM):** Geospatial Information Authority of Japan https://www.gsi.go.jp/
- **Population Census 2020:** e-Stat https://www.e-stat.go.jp/
- **National Accounts:** Cabinet Office of Japan

## Requirements

Python 3.14

```bash
pip install -r requirements.txt
```

## Usage

```bash
python 03_Analysis/scripts/01_data_preparation.py
python 03_Analysis/scripts/02_regression_ols.py
python 03_Analysis/scripts/03_spatial_analysis.py
python 03_Analysis/scripts/04_visualization.py
```

## License

[CC-BY 4.0](LICENSE) — Analysis code and figures

*NDB raw data are not included; available from MHLW (see Data Sources).*

## Zenodo DOI

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

---

## 日本語概要

**研究概要:** 日本全47都道府県を対象に、地形傾斜・都市ウォーカビリティと糖尿病管理指標（HbA1c・BMI肥満率・腹囲・中性脂肪）の関連を生態学的研究で分析しました。NDBオープンデータNo.10（2023年度）を使用し、OLS回帰と条件付き空間ラグモデルを適用しています。

**主な結果:**
- ウォーカビリティは全糖尿病指標で一貫して保護的に関連
- BMI肥満率は強い空間スピルオーバー効果（ρ = 0.753, p < 0.001）を示した
- HbA1cは空間的自己相関がなく、局所的な医療管理要因が優位

**データ:** NDBオープンデータ（厚生労働省）は上記URLより無料で入手可能です。本リポジトリにはNDB生データは含まれません。
```

### 2-4. LICENSE ファイル（CC-BY 4.0）

Creative Commons Attribution 4.0 International（CC-BY 4.0）のライセンステキストを
https://choosealicense.com/licenses/cc-by-4.0/ からコピーして `LICENSE` として保存。

### 2-5. リポジトリを Public に変更

（現在 Private の場合のみ）
1. GitHub → リポジトリ → Settings → Danger Zone
2. `Change visibility` → `Make public`
3. 「I want to make this repository public」と入力して確認

**注意:** Public 化の前に NDB 実データが含まれていないことを必ず確認すること。

---

## 3. Zenodo との連携手順

### 3-1. GitHub → Zenodo 連携

1. https://zenodo.org/ にログイン（GitHub アカウントで連携可）
2. 右上アバター → `GitHub` タブ
3. `Sync` をクリックしてリポジトリ一覧を更新
4. `slope-walkability-diabetes-japan`（リポジトリ名変更後）のトグルを `ON` にする

### 3-2. GitHub Release でDOI取得

1. GitHub → リポジトリ → `Releases` → `Create a new release`
2. Tag version: `v1.0.0`（投稿時または受理後に作成）
3. Release title: `JCH Submission — v1.0.0`
4. Description:

```
Initial public release accompanying manuscript submission to
Journal of Community Health (2026-06-28).

Includes analysis scripts, result figures, and Quarto source.
NDB raw data are not included (available from MHLW).

Key results:
- Walkability protective across all diabetes indicators
- BMI obesity: strong spatial spillover (rho=0.753, p<0.001)
- HbA1c: no spatial autocorrelation (Moran's I=-0.072, p=0.638)
```

5. `Publish release` をクリック

→ Zenodo が自動でアーカイブを作成し、**DOI が発行される**

### 3-3. Zenodo メタデータの編集

Zenodo ダッシュボードでアーカイブのメタデータを編集：

| 項目 | 入力内容 |
|------|---------|
| Title | Topographic Slope, Urban Walkability, and Diabetes in Japan — Analysis Code |
| Authors | [Author 1 Last], [Author 1 First]; [Author 2 Last], [Author 2 First] |
| Description | Analysis code and result figures for the ecological study of slope, walkability, and diabetes across 47 Japanese prefectures. Uses NDB Open Data No.10 (FY2023). |
| Keywords | diabetes; walkability; topographic slope; spatial autocorrelation; NDB; Japan; ecological study |
| License | CC-BY 4.0 |
| Communities | `zenodo`（+ `public-health` があれば追加） |
| Related identifiers | JCH DOI（受理後に追加） |

### 3-4. Data Availability Statement への DOI 追記

DOI 確定後、`Declarations_JCH.md` の Data Availability セクションを更新：

```markdown
Analysis code is openly available at https://github.com/haruki00430/slope-walkability-diabetes-japan
and archived on Zenodo at https://doi.org/10.5281/zenodo.XXXXXXX (CC-BY 4.0).
```

その後 `convert_to_jch_format.py` を再実行して `Manuscript_JCH.docx` を更新する。

---

## 4. 既存公開プロジェクトとの対応表

| 既存プロジェクト | GitHub 名 | Zenodo DOI |
|--------------|-----------|-----------|
| slope_fracture | `slope-fracture-japan`（推定） | 10.5281/zenodo.20452953 |
| diabetes_unemployment | `ndb-unemployment-diabetes-japan` | 10.5281/zenodo.20949288 |
| pollen_allergy_v2 | （確認要） | （確認要） |
| **slope_diabetes（本プロジェクト）** | `slope-walkability-diabetes-japan`（予定） | TBD |

---

## 5. チェックリスト（GitHub / Zenodo）

### 論文投稿前
- [ ] リポジトリ名を `slope-walkability-diabetes-japan` に変更
- [ ] NDB 実データが含まれていないことを確認
- [ ] README.md（英日）を整備
- [ ] LICENSE ファイルを配置（CC-BY 4.0）
- [ ] .gitignore を確認
- [ ] リポジトリを Public に変更
- [ ] Zenodo 連携を有効化
- [ ] GitHub Release v1.0.0 を作成（投稿と同時）
- [ ] Zenodo で DOI を取得
- [ ] Zenodo メタデータを編集

### 論文受理後
- [ ] Data Availability Statement に Zenodo DOI を追記
- [ ] Manuscript_JCH.docx を更新して最終提出
- [ ] Zenodo メタデータに Journal DOI を追加（Related identifiers）

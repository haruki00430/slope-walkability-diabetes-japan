# JCH 投稿チェックリスト
# Journal of Community Health — Submission Checklist
# 作成日: 2026-06-28

---

## A. 投稿前・著者情報の確認

- [ ] 全著者の実名が記載されている（プレースホルダー `[Author 1]` を置き換え済み）
- [ ] 全著者の所属（英語）が正確に記載されている
- [ ] 対応著者のメールアドレスが記載されている
- [ ] 全著者の ORCID が確認・記載されている（なければ https://orcid.org/ で取得）
- [ ] 著者順序が全員の合意を得ている

---

## B. 原稿フォーマット（JCH 投稿規定 準拠）

### 全般
- [ ] Word (.docx) 形式で保存されている
- [ ] 欧文フォント: Times New Roman 12pt、ダブルスペース
- [ ] ページ番号あり（右下）
- [ ] 行番号あり（連続）
- [ ] 余白: 2.5cm（全辺）

### 構成要素（Manuscript DOCX 本文のみ）
- [ ] Abstract（150–250 words）が structured format（Background/Objective/Methods/Results/Conclusions）になっている
- [ ] Abstract 内に未定義の略語がない
- [ ] Keywords が 4–6 個（セミコロン区切り）
- [ ] 本文：Introduction → Methods → Results → Discussion → Conclusions
- [ ] Declarations（Funding, COI, Ethics, Consent, Data Availability, Author Contributions）が References の前にある
- [ ] Figure Captions が本文末尾（References 後）にまとめてある
- [ ] Tables が本文中（言及箇所の直後）または本文末尾にある

### 引用形式（重要）
- [ ] **本文内引用**: `[1]` 形式（角括弧、通し番号）← Vancouver `1)` から変換済み
- [ ] **参照リスト**: APA-7 形式（著者 年. タイトル. *斜体誌名*, *巻*(号), ページ. https://doi.org/xxx）
- [ ] 参照番号が文中の出現順に [1]〜[35] となっている
- [ ] 全参照に DOI または URL が記載されている

---

## C. Abstract ワード数確認

> TitlePage_JCH.md のAbstract（約 210 words）で JCH 要件（150–250 words）を満たす。

- [ ] Abstract を word count ツールで確認（150–250 words）

---

## D. Keywords

現在の Keywords（6個）: `built environment; walkability; diabetes; spatial autocorrelation; ecological study; Japan`

- [ ] Keywords が 4–6 個の範囲内（現在: 6個 ✓）
- [ ] Keywords が Abstract 中に登場する
- [ ] セミコロン区切りで記載

---

## E. Figures（JCH 要件）

| 図番号 | ファイル名 | 内容 | 解像度確認 |
|--------|-----------|------|----------|
| Fig. 1 | `Fig1.png` | Study overview map | ≥300 dpi |
| Fig. 2 | `Fig2.png` | Forest plot | ≥300 dpi |
| Fig. 3 | `Fig3.png` | Scatter grid | ≥300 dpi |
| Fig. 4 | `Fig4.png` | Spatial autocorrelation | ≥300 dpi |

- [ ] 各 Figure ファイルの解像度が ≥300 dpi（halftone: 300; combination art: 600 dpi）
- [ ] Figure Captions が "**Fig. 1**" 形式（太字、ピリオドあり、末尾句点なし）
- [ ] 全 Figure が本文中で言及されている（"Figure 1" → "Fig. 1"）
- [ ] カラー Figure の場合、オープンアクセスでないため白黒印刷でも判読可能か確認

### Figure Captions（DOCX に含む）

```
Fig. 1 Geographic distribution of key variables across 47 Japanese prefectures. Maps show
prefecture-level spatial patterns of (a) topographic slope (mean degrees), (b) walkability
index (Z-score), (c) HbA1c (%), and (d) BMI obesity rate (%). Data sources: NDB Open Data
No.10 (fiscal year 2023), Geospatial Information Authority of Japan, Population Census 2020

Fig. 2 Forest plot of regression coefficients (β) from ordinary least squares (OLS) models
for four diabetes-related outcomes. Walkability showed consistently negative (protective)
associations across all outcomes; topographic slope showed significant associations with
BMI obesity rate and waist circumference

Fig. 3 Scatter plots of walkability index versus four diabetes-related outcome variables
across 47 Japanese prefectures. Lines indicate ordinary least squares regression fits with
95% confidence intervals

Fig. 4 Spatial autocorrelation analysis for BMI obesity rate. (a) Moran scatterplot
(Moran's I = 0.519, p < 0.0001); (b) LISA cluster map showing High-High clusters in
northeastern and southern Japan; (c) residual spatial autocorrelation of OLS model;
(d) comparison of model performance (OLS vs Spatial Lag Model)
```

---

## F. Tables（JCH 要件）

- [ ] Table タイトルが表の上にある
- [ ] 脚注（略語説明）が表の下にある
- [ ] 表内で使用した略語が脚注で定義されている
- [ ] 表が本文内で言及されている

---

## G. Declarations（必須）

- [ ] Funding statement 記載済み（"No funding"）
- [ ] Competing interests 記載済み（"No competing interests"）
- [ ] Ethics approval 記載済み（aggregate data; no IRB required）
- [ ] Consent to Participate 記載済み（"Not applicable"）
- [ ] Consent for Publication 記載済み（"Not applicable"）
- [ ] Data Availability 記載済み（GitHub URL + Zenodo DOI）
- [ ] Authors' Contributions 記載済み（CRediT taxonomy）

---

## H. セキュリティ確認

- [ ] NDB 実データが DOCX・supplementary に含まれていない
- [ ] 個人情報・施設名等が含まれていない
- [ ] GitHub リポジトリに NDB 生データが含まれていない（`02_Data/raw/` が `.gitignore` に記載）
- [ ] `02_Data/raw/` を変更していない

---

## I. GitHub / Zenodo 準備

- [ ] GitHub リポジトリ（https://github.com/haruki00430/slope-walkability-diabetes-japan）が Public になっている
- [ ] README.md（英語・日本語）が整備されている
- [ ] LICENSE ファイル（CC-BY 4.0）が配置されている
- [ ] .gitignore に NDB データ・設定フォルダが記載されている
- [ ] Zenodo 連携が有効化されている
- [ ] Zenodo DOI が取得済み（または投稿後に取得予定）

---

## J. 最終チェック

- [ ] Manuscript_JCH.docx の引用番号が連続（[1]〜[34]、飛びなし）
- [ ] 参照リストに 34 件あり、番号と本文の対応が正しい（旧[22] Nguyen 削除済み）
- [ ] DOCX をPDF 変換してレイアウトを目視確認
- [ ] Spell check（英語）を実行済み
- [ ] Abstract を別の人が確認済み（第二著者レビュー）

---

## 提出完了後

- [ ] Manuscript ID を記録: `JOCE-D-26-_______`
- [ ] 確認メールを保存
- [ ] MEMORY.md または論文管理ファイルに投稿日・Manuscript ID を記録

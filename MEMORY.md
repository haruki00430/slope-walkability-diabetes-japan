# MEMORY — NDB_XXX_slope_diabetes

プロジェクト運用メモ（投稿状況・次アクション・記録用）。  
正本リポジトリ: https://github.com/haruki00430/slope-walkability-diabetes-japan

**最終更新**: 2026-07-07

---

## 論文概要

| 項目 | 内容 |
|------|------|
| **英語タイトル** | Outcome-Specific Spatial Dependence of Metabolic Health: Obesity Exhibits Regional Dependence Whereas Glycemic Control Does Not |
| **著者** | Haruki Saito (通信), Tetsuya Ohira |
| **通信著者メール** | m211039@fmu.ac.jp |
| **ORCID (Saito)** | 0009-0009-7890-6068 |
| **ORCID (Ohira)** | 0000-0003-4532-7165 |
| **データ年度** | NDB Open Data No.10（FY2023） |
| **コードアーカイブ** | https://doi.org/10.5281/zenodo.21237968（v1.0.1, 2026-07-07） |

---

## 投稿状況（現行）— Health & Place (JHAP)

| 項目 | 内容 |
|------|------|
| **雑誌** | Health & Place (Elsevier, ISSN 1353-8292) |
| **ステータス** | **投稿パッケージ準備完了**（EM 未投稿） |
| **投稿システム** | Editorial Manager — https://www.editorialmanager.com/jhap/ |
| **パッケージ** | `04_Manuscripts/submission_package_JHAP/` |

### 準備済みファイル

| ファイル | 用途 |
|---------|------|
| `Manuscript_JHAP_anonymized.docx` | 匿名原稿（**規定必須の2点のみ** ORCP から追加） |
| `TitlePage_JHAP.docx` | タイトルページ（CRediT・謝辞・Funding 含む） |
| `CoverLetter_JHAP.docx` | カバーレター（JCH・ORCP 謝絶開示済み） |
| `Highlights_JHAP.docx` | Highlights（5項目） |
| `Declaration_of_Interest_JHAP.docx` | 利益相反宣言 |
| `STROBE_Checklist_JHAP.docx` | STROBE チェックリスト |
| `Fig1.png` / `Fig2.png` / `Fig3.png` | 図（ORCP から流用） |
| `SupplementaryFig1.png` | 補足図 |

### 注意（投稿前）

- **語数:** 本文約2,000語 — H&P 推奨 4,000–6,000語を下回る（拡充検討）
- **Graphical Abstract:** H&P では不要（ORCP 版は含めない）
- 詳細: `JHAP_Submission_Checklist_20260707.md`

---

## 投稿状況（前誌）— Obesity Research & Clinical Practice (ORCP)

| 項目 | 内容 |
|------|------|
| **雑誌** | Obesity Research & Clinical Practice (Elsevier, ISSN 1871-403X) |
| **Manuscript ID** | **ORCP-D-26-00394** |
| **Article Type** | Research Paper (Original Research Article) |
| **投稿日時** | 2026-06-30 21:41 JST |
| **判定日時** | **2026-07-07 18:04 JST** |
| **ステータス** | **Desk reject**（査読未実施・Editor-in-Chief 判定） |
| **判定者** | Professor Kuo-Chin Huang（Editor-in-Chief） |
| **投稿システム** | Editorial Manager — https://www.editorialmanager.com/orcp/ |
| **審査所要** | 約7日（投稿〜判定） |

### 編集決定の要旨

> *Unfortunately your manuscript has not received a high enough priority to be sent for review, and accordingly we are unable to accept it for publication.*

- **査読コメントなし**（優先度不足による編集拒否）
- 品質への言及は定型的（「品質を反映しない」旨の一文のみ）
- **Article Transfer の具体的案内は本メールにはなし**

### 判定メールの証跡

| ファイル | 用途 |
|---------|------|
| `04_Manuscripts/submission_package_ORCP/Gmail - Decision on submission to Obesity Research & Clinical Practice.pdf` | **編集拒否メール**（2026-07-07 18:04） |
| `04_Manuscripts/submission_package_ORCP/Gmail - ORCP-D-26-00394 - Confirming your submission to Obesity Research & Clinical Practice.pdf` | 受付確認メール（2026-06-30 21:41） |
| `04_Manuscripts/submission_package_ORCP/ORCP-S-26-00548 (1).pdf` | **投稿パッケージ正本**（記号修正済み・33頁） |
| `04_Manuscripts/submission_package_ORCP/ORCP-S-26-00548.pdf` | 投稿直後ドラフトPDF（`35?` / `¥` 文字化けあり・参照用） |
| `04_Manuscripts/submission_package_ORCP/Manuscript_ORCP_anonymized.docx` | 匿名原稿正本（`fix_orcp_manuscript_symbols.py` 適用済み） |

### EM アップロードファイル（記録）

| ファイル | EM Item Type |
|---------|--------------|
| `CoverLetter_ORCP.docx` | Cover Letter |
| `TitlePage_ORCP.docx` | Title Page |
| `Manuscript_ORCP_anonymized.docx` | Manuscript File |
| `Declaration_of_Interest_ORCP.docx` | Declaration of Interest |
| `Ethical_Statement_ORCP.docx` | Ethical Statement |
| `Author_Agreement_ORCP.docx` | Author Agreement |
| `STROBE_Checklist_ORCP.docx` | Reporting Guidelines Checklist |
| `Highlights_ORCP.docx` | Highlights |
| `GraphicalAbstract_ORCP.png` | Graphical Abstract |
| `Fig1.png` / `Fig2.png` / `Fig3.png` | Figure（各1回） |
| `SupplementaryFig1.png` | Supplementary Figure |

### メタデータ（EM 入力記録）

- **Keywords（6語）**: built environment; walkability; diabetes; spatial autocorrelation; ecological study; Japan
- **Classifications（5）**: Obesity; Epidemiology; Physical Activity; Prevention; Environmental Factor
- **Contributors**: Saito（Corresponding / First）→ Ohira（Supervision, Writing – review & editing）

---

## 次のアクション

| 優先度 | アクション |
|--------|-----------|
| 高 | **EM 投稿**（https://www.editorialmanager.com/jhap/） |
| 高 | **GitHub push** + Zenodo v1.0.1 | **完了**（2026-07-07） |
| 高 | Data availability / Title Page / README の DOI を `10.5281/zenodo.21237968` に更新 | **完了**（2026-07-07） |
| 中 | 投稿後 PDF プレビューで `°` / `¥` 文字化け確認 |
| 低 | ORCP EM でステータス *Rejected* を確認・記録 |

### 注意

- **他誌への再投稿は可能**（desk reject のため改訂義務なし。ただし投稿履歴の開示は必須）
- 詐欺メール（受理前 APC 請求等）に注意

---

## 投稿履歴（前誌）

| 雑誌 | Manuscript ID | 投稿日 | 結果 | 備考 |
|------|---------------|--------|------|------|
| Journal of Community Health (JCH) | JOHE-D-26-01791 | 2026-06-28頃 | **Desk reject**（2026-06-30） | ORCP カバーレターに開示済み |
| **Obesity Research & Clinical Practice** | **ORCP-D-26-00394** | **2026-06-30** | **Desk reject**（**2026-07-07**） | 査読なし・EiC判定 |

---

## 投稿パッケージ内の重要スクリプト

| スクリプト | 用途 |
|-----------|------|
| `create_jhap_em_docx.py` | ORCP 正本コピー + カバーレター必須差分 + 宣言類日付 |
| `fix_jhap_manuscript_for_submission.py` | 原稿: Data availability（初回適用） |
| `fix_jhap_fig3_map_caption.py` | Fig.3 埋め込みキャプション地図注記 |
| `Zenodo_Update_JHAP_v1.0.1.md` | Zenodo v1.0.1 メタデータ更新手順 |

**使用禁止**: `fix_orcp_manuscript_layout.py`（フォント一括変更でスタイル破壊）

---

## 修正履歴（投稿関連）

| 日付 | 内容 |
|------|------|
| 2026-06-30 | JCH → ORCP 転投稿パッケージ整備 |
| 2026-06-30 | 図番号リナンバリング（Fig. 1–3）、Title Page・Cover Letter 修正 |
| 2026-06-30 | EM 必須7 DOCX 作成、Graphical Abstract レイアウト改善 |
| 2026-06-30 | 原稿 DOCX の `35?` / `¥` 文字化け修正（`fix_orcp_manuscript_symbols.py`） |
| 2026-06-30 | **ORCP-D-26-00394 投稿完了**（21:41 JST） |
| 2026-07-07 | **ORCP desk reject**（ORCP-D-26-00394、査読なし） |
| 2026-07-07 | **Zenodo v1.0.1 発行** — https://zenodo.org/records/21237968（DOI: 10.5281/zenodo.21237968） |

# Editorial Manager アップロード順序ガイド
# Journal of Community Health — Springer Nature

**投稿先**: https://www.editorialmanager.com/joce/  
**投稿日**: 2026-06-28（目標）

---

## 事前確認チェックリスト

- [ ] 著者名・所属をプレースホルダー `[Author 1]` から実名に置き換え済み
- [ ] ORCID を取得・記載済み
- [ ] 対応著者メールアドレスを記載済み
- [ ] Zenodo DOI を取得済み（または「TBD」のまま投稿）
- [ ] Manuscript_JCH.docx が最新版であることを確認

---

## ファイルアップロード順序（Editorial Manager 推奨順）

| 順番 | ファイル種別 | ファイル名 | 備考 |
|------|------------|-----------|------|
| 1 | **Cover Letter** | `CoverLetter_JCH.md` の内容をテキスト貼り付け | Springer のカバーレター欄 |
| 2 | **Title Page** | `TitlePage_JCH.md` を DOCX 化してアップロード | 著者情報あり・匿名でない |
| 3 | **Manuscript** | `Manuscript_JCH.docx` | 本文・Tables・Figure Captions を含む |
| 4 | **Figure 1** | `Fig1.png` | ≥300 dpi（study overview map） |
| 5 | **Figure 2** | `Fig2.png` | ≥300 dpi（forest plot） |
| 6 | **Figure 3** | `Fig3.png` | ≥300 dpi（scatter grid） |
| 7 | **Figure 4** | `Fig4.png` | ≥300 dpi（spatial autocorrelation） |

> **注意**: Springer Nature の Editorial Manager では、Figure はそれぞれ「Figure」カテゴリで個別にアップロードする。まとめてアップロード不可。

---

## Editorial Manager 操作手順

### Step 1: アカウントとジャーナル選択

1. https://www.editorialmanager.com/joce/ にアクセス
2. 「Author Login」→ アカウント作成 or ログイン
3. 「Submit New Manuscript」をクリック

### Step 2: Article Type

- Article Type: **Original Article**（または Research Article）
- Special Issue: 該当しない場合は空欄

### Step 3: Title & Abstract

- Title: `Association between Topographic Slope, Urban Walkability, and Diabetes Management Indicators: An Ecological Study of 47 Japanese Prefectures`
- Running title: `Slope, Walkability, and Diabetes in Japan`（≤60 characters）
- Abstract: TitlePage_JCH.md の Abstract をコピー貼り付け
- Keywords: `built environment; walkability; diabetes; spatial autocorrelation; ecological study; Japan`（6個）

### Step 4: Authors

各著者について以下を入力：

| 項目 | 内容 |
|------|------|
| First Name | 実名 |
| Last Name | 実名 |
| Institution | 所属機関名（英語） |
| Department | 学科・専攻名（英語） |
| Country | Japan |
| Email | メールアドレス |
| ORCID | 0000-0000-0000-0000 |
| Corresponding? | 対応著者に ✓ |

### Step 5: Cover Letter

`CoverLetter_JCH.md` の本文（---以下）をコピー貼り付け。

### Step 6: Manuscript Files Upload

以下の順序でファイルをアップロードする：

1. **Manuscript** カテゴリ → `Manuscript_JCH.docx`
   - 本文（Introduction〜References）を含む
   - Figure Captions を本文末尾に含む
   - Tables を本文中または末尾に含む
   - **著者情報・謝辞を含まない**（blind review対応）

2. **Title Page** カテゴリ → `TitlePage_JCH.docx`（TitlePage_JCH.md から作成）

3. **Figure** カテゴリ × 4 → `Fig1.png` 〜 `Fig4.png`
   - 各 Figure を個別にアップロード
   - Caption は Manuscript DOCX 内に記載（図ファイルには不要）

### Step 7: Statements & Declarations

Editorial Manager 内の各フォームに以下を入力：

| フォーム項目 | 入力内容 |
|------------|---------|
| Funding | No funding was received. |
| Conflict of Interest | No competing interests. |
| Ethics Approval | NDB Open Data; publicly available aggregate data; no approval required |
| Data Availability | Code at https://github.com/haruki00430/NDB_XXX_slope_diabetes |
| AI Use | Claude Code, Cursor used for scripting; verified by authors |

### Step 8: Suggested Reviewers（任意）

JCH では査読者を提案できる場合がある。空欄でも可。

### Step 9: 最終確認と提出

1. PDF プレビューで全ファイルを確認
2. 図が正しく表示されているか確認
3. 参考文献の形式が [1]〜[35] になっているか確認
4. 「Submit」ボタンをクリック
5. 確認メール（Manuscript ID）を受信・保存

---

## 提出後の確認事項

- [ ] Manuscript ID を記録（例: `JOCE-D-26-XXXXX`）
- [ ] 確認メールを保存
- [ ] 査読回答期限を確認（通常 4〜8 週間）

---

## このパッケージに含まれるファイル一覧

```
submission_package_JCH/
├── CoverLetter_JCH.md           ← カバーレター（テキスト貼り付け用）
├── TitlePage_JCH.md             ← タイトルページ（DOCX化してアップロード）
├── Declarations_JCH.md          ← Declarations + APA-7 参照リスト（本文挿入用）
├── Manuscript_JCH.docx          ← 本文 DOCX（convert_to_jch_format.py で生成）
├── Manuscript_JCH_backup_20260628.docx  ← バックアップ
├── Fig1.png                     ← Study overview map
├── Fig2.png                     ← Forest plot
├── Fig3.png                     ← Scatter grid
├── Fig4.png                     ← Spatial autocorrelation
├── README_UPLOAD_ORDER.md       ← このファイル
├── JCH_Submission_Checklist_20260628.md ← 提出チェックリスト
├── GitHub_Zenodo_Setup_Guide.md ← GitHub/Zenodo 設定手順
├── convert_to_jch_format.py     ← 引用形式変換スクリプト
└── Submission guidelines _ Journal of Community Health _ Springer Nature Link.pdf
```

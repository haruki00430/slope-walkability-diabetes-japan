# Health & Place — Submission Package (JHAP)

**Target journal:** Health & Place (Elsevier, ISSN 1353-8292)  
**EM URL:** https://www.editorialmanager.com/jhap/  
**Package prepared:** 2026-07-07

---

## Files for Editorial Manager

| File | EM Item Type |
|------|--------------|
| `CoverLetter_JHAP.docx` | Cover Letter |
| `TitlePage_JHAP.docx` | Title Page |
| `Manuscript_JHAP_anonymized.docx` | Manuscript (anonymized) |
| `Declaration_of_Interest_JHAP.docx` | Declaration of Interest |
| `Ethical_Statement_JHAP.docx` | Ethical Statement (optional backup) |
| `STROBE_Checklist_JHAP.docx` | Reporting Guidelines Checklist |
| `Highlights_JHAP.docx` | Highlights |
| `Fig1.png` / `Fig2.png` / `Fig3.png` | Figure (each once) |
| `SupplementaryFig1.png` | Supplementary Figure |

**Not required for H&P (vs ORCP):** Graphical Abstract

---

## EM Metadata (draft)

- **Article type:** Full Length Article / Original Research
- **Keywords (6):** built environment; walkability; diabetes; spatial autocorrelation; ecological study; Japan
- **Region of Origin:** Asia Pacific
- **Prior submissions (disclose):**
  - JCH: JOHE-D-26-01791 (desk reject 2026-06-30)
  - ORCP: ORCP-D-26-00394 (desk reject 2026-07-07)

---

## Regenerate scripts

```bash
python create_jhap_em_docx.py              # 宣言類日付・カバーレター
python fix_jhap_manuscript_for_submission.py  # Data availability（初回のみ）
python fix_jhap_fig3_map_caption.py        # Fig.3 埋め込みキャプション地図注記
```

**方針:** 規定で必須の修正以外は変更しない。ORCP 正本（`submission_package_ORCP/`）がベース。

---

## Guide compliance summary

| Requirement | Status |
|-------------|--------|
| Double-anonymized review (separate Title Page) | OK（ORCP 正本コピー） |
| Abstract ≤250 words | OK（変更なし） |
| Keywords 1–7 | OK（変更なし） |
| Highlights 3–5, ≤85 chars | OK（ORCP 正本コピー） |
| **Data availability** in manuscript | OK（**追加のみ**） |
| Generative AI disclosure | OK（ORCP から変更なし） |
| CRediT on Title Page | OK（ORCP 正本コピー） |
| **Map boundary note** (Fig. 3 LISA + embedded caption) | OK |
| Body 4,000–6,000 words | ⚠ ~2,000 words（原稿本文は未変更） |

See `JHAP_Submission_Checklist_20260707.md` for full checklist.

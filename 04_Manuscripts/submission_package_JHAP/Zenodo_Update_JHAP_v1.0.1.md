# Zenodo メタデータ更新 — Health & Place 投稿（v1.0.1）

**日付:** 2026-07-07  
**既存 DOI（変更なし）:** https://doi.org/10.5281/zenodo.20989085  
**GitHub:** https://github.com/haruki00430/slope-walkability-diabetes-japan

---

## 方針

- **v1.0.0**（2026-06-28, JCH 投稿時）はそのまま残す
- **v1.0.1** を新規リリースし、Zenodo メタデータを H&P 投稿向けに更新する
- コード内容の変更は不要（README 更新のみを含む場合あり）
- 原稿本文・Data availability の DOI URL は **変更不要**（同一 DOI コンセプトレコード）

---

## 手順 A: GitHub Release v1.0.1

1. README の H&P 向け更新を commit & push
2. GitHub → Releases → **Draft a new release**
3. **Tag:** `v1.0.1`
4. **Title:** `Health & Place Submission — v1.0.1`
5. **Description**（以下をコピー）:

```
Metadata update accompanying manuscript submission to Health & Place (2026-07-07).

Previously submitted to:
- Journal of Community Health (JOHE-D-26-01791, desk reject 2026-06-30)
- Obesity Research & Clinical Practice (ORCP-D-26-00394, desk reject 2026-07-07)

Includes analysis scripts and result figures for a prefecture-level spatial
epidemiology study (47 Japanese prefectures, NDB Open Data FY2023).
NDB raw data are not included (available from MHLW).

Key results:
- Outcome-specific spatial dependence (obesity vs glycemic control)
- BMI obesity: Moran's I = 0.519; spatial lag rho = 0.753 (p < 0.001)
- HbA1c: no spatial autocorrelation (Moran's I = -0.072, p = 0.638)
```

6. **Publish release** → Zenodo が自動アーカイブ（GitHub 連携 ON の場合）

---

## 手順 B: Zenodo ダッシュボードでメタデータ編集

https://zenodo.org/records/20989085 → **New version** または v1.0.1 レコードを編集

| 項目 | 入力内容 |
|------|---------|
| **Title** | Outcome-Specific Spatial Dependence of Metabolic Health — Analysis Code (Health & Place submission) |
| **Publication date** | 2026-07-07 |
| **Version** | v1.0.1 |
| **Description** | 下記「Description 全文」を使用 |
| **Keywords** | spatial epidemiology; health geography; walkability; diabetes; obesity; Moran's I; ecological study; Japan; NDB |
| **License** | CC-BY 4.0 |
| **Related identifiers** | `https://github.com/haruki00430/slope-walkability-diabetes-japan/tree/v1.0.1` (isSupplementTo, software) |

### Description 全文（HTML 可）

```html
<p>Analysis code and result figures for the manuscript
&quot;Outcome-Specific Spatial Dependence of Metabolic Health: Obesity Exhibits
Regional Dependence Whereas Glycemic Control Does Not&quot;,
submitted to <em>Health &amp; Place</em> (2026-07-07).</p>

<p>Previously submitted to <em>Journal of Community Health</em>
(Manuscript ID: JOHE-D-26-01791) and <em>Obesity Research &amp; Clinical Practice</em>
(Manuscript ID: ORCP-D-26-00394).</p>

<p>Cross-sectional ecological study of 47 Japanese prefectures using NDB Open Data
No.10 (FY2023). NDB raw data are not included (available from MHLW).</p>

<p><strong>Key results:</strong></p>
<ul>
<li>BMI obesity: strong regional clustering (Moran's I = 0.519)</li>
<li>Spatial lag model for obesity (rho = 0.753, p &lt; 0.001)</li>
<li>HbA1c: no spatial autocorrelation (Moran's I = -0.072, p = 0.638)</li>
</ul>
```

---

## 手順 C: 確認

- [ ] https://doi.org/10.5281/zenodo.20989085 が v1.0.1 を指す（または Latest version に v1.0.1 が表示）
- [ ] Zenodo タイトル・説明に JCH/ORCP のみでなく H&P が記載されている
- [ ] GitHub README の Citation が H&P と一致

---

## 注意

- Zenodo の **concept DOI** `10.5281/zenodo.20989084` は全バージョン共通
- 原稿中の `https://doi.org/10.5281/zenodo.20989085` は concept DOI または version DOI のどちらでも可（現状維持で可）

# 実装計画書: NDB_XXX_slope_diabetes

## プロジェクト概要

**研究タイトル:** 地形傾斜度・歩行環境が2型糖尿病管理指標に与える影響：47都道府県の横断的生態学的研究

**研究目的:** 地形傾斜度と歩行環境が糖尿病管理指標（HbA1c, BMI等）に与える影響を都道府県レベルで検証する

**研究デザイン:** 横断的生態学的研究（N=47都道府県）

**データソース:** NDBオープンデータ第10回（2021年度診療分）+ 令和2年国勢調査 + DEM地形データ

---

## 実装フェーズ

### Phase 0: プロジェクトセットアップ ✅ 完了
- ディレクトリ構造作成
- config.yaml作成
- ドキュメントファイル作成

### Phase 1: NDB特定健診データ抽出
- **Phase 1a:** 検査データ（HbA1c, BMI, 腹囲, 中性脂肪）
- **Phase 1b:** 質問票データ（Q3, Q4 運動習慣）

### Phase 2: 地形データ統合 ✅ 完了
- **Phase 2a:** `projects/NDB_XXX_slope_fracture/03_Analysis/data/interim/slope_by_prefecture_final.csv` を再利用（25都道府県）
- **Phase 2b:** `projects/NDB_XXX_slope_fracture/03_Analysis/data/processed/analysis_dataset_v1.csv` から全47都道府県分の地形データを取得・補完

### Phase 3: 外部データ取得
- **Phase 3a:** 人口密度・DID比率（令和2年国勢調査）
- **Phase 3b:** 社会経済変数（所得、失業率、高齢化率）
- **Phase 3c:** 都道府県境界GeoJSON（A38から集約）

### Phase 4: データ統合
- 全データソース統合
- `analysis_dataset_full.csv` (N=47) 作成（地形データ含む全変数）

### Phase 5: 探索的データ解析
- 記述統計（Table 1）
- 相関行列
- 欠損データ比較

### Phase 6: 統計解析
- **Phase 6a:** OLS回帰モデル
- **Phase 6b:** 空間分析（Moran's I有意時のみ）

### Phase 7: 感度分析（オプション）
- 傾斜度欠損vs完全データ比較
- 歩行環境指標の代替案

### Phase 8: 可視化
- Figure 1: 研究概要マップ
- Figure 2: Forest plot
- Figure 3: 散布図
- Figure 4: 空間的自己相関（条件付き）

### Phase 9: 論文作成
- Quarto原稿 (.qmd)
- 参考文献（Vancouver形式）
- HTML・DOCX出力

---

## 重要な設計判断

### 1. 地形データの取得（変更）
- **判断:** slope_fracture最終データから全47都道府県分を取得（当初計画のN=25から変更）
- **理由:** slope_fractureプロジェクトで既に47都道府県分のDEM処理が完了済み；主要解析・二次解析ともN=47で統一可能

### 2. 歩行環境の測定
- **計算式:** `(zscore(人口密度) + zscore(DID比率)) / 2`
- **構成要素:** 人口密度 + DID比率（令和2年国勢調査）

### 3. 空間分析戦略
- **戦略:** 条件付き（検定→適用）
- **ワークフロー:** OLS → Moran's I → LMテスト → SLM/SEM（有意時のみ）

### 4. 調整変数
- **Tier 1（必須）:** 高齢化率、所得、失業率、運動習慣
- **VIF閾値:** < 5.0

---

## タイムライン

- **Phase 0:** 2時間 ✅ 完了
- **Phase 1:** 4時間（NDB抽出）
- **Phase 2:** 1時間（地形統合）
- **Phase 3:** 8-12時間（外部データ、ボトルネック）
- **Phase 4:** 2時間（データ統合）
- **Phase 5:** 4時間（EDA）
- **Phase 6:** 6時間（統計解析）
- **Phase 7:** 4時間（感度分析、オプション）
- **Phase 8:** 6時間（可視化）
- **Phase 9:** 8時間（論文）

**合計:** 40-50時間（5-6営業日）

---

## 検証チェックリスト

- [x] Phase 1: examination_outcomes.csvで47都道府県確認 ✅
- [x] Phase 2: 傾斜度データ全47都道府県確認 ✅
- [ ] Phase 3: 歩行環境指数範囲（-2～+2、Z-score標準化後）確認
- [ ] Phase 4: 統合データセット47行、重複なし確認
- [ ] Phase 5: 相関行列で|r| > 0.7なし確認
- [ ] Phase 6a: 全モデルでVIF < 5.0確認
- [ ] Phase 6b: Moran's I範囲（-1～+1）確認
- [ ] Phase 8: 日本語フォント正常表示（□□□なし）確認
- [ ] Phase 9: QuartoのDOCX出力エラーなし確認

---

詳細な実装計画は以下を参照: `C:\Users\user\.claude\plans\spicy-coalescing-sundae.md`

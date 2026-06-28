"""
convert_to_jch_format.py
------------------------
Journal of Community Health (JCH) 投稿用 DOCX 変換スクリプト

【処理内容】
1. Vancouver 形式 "n)" の本文内引用 → JCH 形式 "[n]" に変換
2. 複合引用 "n), m)" → "[n, m]" に変換
3. Declarations セクションを References の直前に挿入
4. 出力: submission_package_JCH/Manuscript_JCH.docx

【使用方法】
    python convert_to_jch_format.py

【依存関係】
    pip install python-docx

【注意】
    - 参照リストの APA-7 変換は手動（Declarations_JCH.md を参照）
    - References セクション以降の置き換えは行わない
    - 図表のキャプション内の引用も変換される
"""

import re
import shutil
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.oxml.ns import qn
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    print("ERROR: python-docx が必要です。")
    print("       pip install python-docx  を実行してインストールしてください。")
    raise

# ============================================================
# パス設定
# ============================================================
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # NDB_XXX_slope_diabetes/

# 入力: バックアップ DOCX（元ファイルを保護）
INPUT_DOCX = SCRIPT_DIR / "Manuscript_JCH_backup_20260628.docx"

# 出力: JCH 形式 DOCX
OUTPUT_DOCX = SCRIPT_DIR / "Manuscript_JCH.docx"

# Declarations テキストファイル（Declarations_JCH.md の内容を参照）
DECLARATIONS_MD = SCRIPT_DIR / "Declarations_JCH.md"


# ============================================================
# 引用形式変換: "n)" → "[n]"
# ============================================================

# 本文内引用パターン（Vancouver 形式の数字引用）
#
# 【変換対象】
#   word4)         → word[4]       （単語直後）
#   methodology,4) → methodology,[4]（カンマ後）
#   I.11)          → I.[11]        （略語ピリオド後）
#   likelihood.9)  → likelihood.[9] （文末ピリオド後）
#   2020.10)       → 2020.[10]     （4桁年+ピリオド後）
#   8), 9)         → [8, 9]        （複合引用）
#
# 【変換対象外（偽陽性防止）】
#   0.05)  0.437)  0.001)  などの小数値・p値・係数
#   (N = 47)  (2020)  (2023) などの記述的括弧
#
# 識別ロジック:
#   単独引用は「直前が英字/句読点/閉じ括弧」の場合のみ変換。
#   小数値は前が数字 → 不一致でスキップ。
CITATION_PATTERNS = [
    # 4連続引用: "n), m), k), l)" → "[n, m, k, l]"
    (
        re.compile(r'(\d+)\),\s*(\d+)\),\s*(\d+)\),\s*(\d+)\)'),
        r'[\1, \2, \3, \4]'
    ),
    # 3連続引用: "n), m), k)" → "[n, m, k]"
    (
        re.compile(r'(\d+)\),\s*(\d+)\),\s*(\d+)\)'),
        r'[\1, \2, \3]'
    ),
    # 2連続引用: "n), m)" → "[n, m]"
    (
        re.compile(r'(\d+)\),\s*(\d+)\)'),
        r'[\1, \2]'
    ),
    # 範囲引用: "n)-m)" → "[n-m]"
    (
        re.compile(r'(\d+)\)-(\d+)\)'),
        r'[\1-\2]'
    ),
    # 単独引用①: 英字+ピリオド+引用番号 "I.11)" "likelihood.9)"
    #   lookbehind=英字、次に '.' を含む match → ".[\1]"
    (
        re.compile(r'(?<=[a-zA-Z])\.(\d{1,2})\)(?!\d)'),
        r'.[\1]'
    ),
    # 単独引用②: 4桁年+ピリオド+引用番号 "2020.10)"
    (
        re.compile(r'(?<=\d{4})\.(\d{1,2})\)(?!\d)'),
        r'.[\1]'
    ),
    # 単独引用③: 英字/カンマ/セミコロン/]/閉じ括弧の直後 "word4)" ",4)" ")2)"
    #   ※ 前が数字や小数点の場合は除外（p値・係数の保護）
    (
        re.compile(r'(?<=[a-zA-Z,;!?\]\)])(\d{1,2})\)(?!\d)'),
        r'[\1]'
    ),
]


def convert_citations_in_text(text: str) -> str:
    """
    テキスト内のVancouver形式引用をJCH形式に変換する（最大3パス）。
    References セクション以降のテキストは変換しない（呼び出し元で制御）。
    5連続以上の引用は2パス目以降で残存を吸収する。
    """
    for _ in range(3):
        prev = text
        for pattern, replacement in CITATION_PATTERNS:
            text = pattern.sub(replacement, text)
        if text == prev:
            break  # 変更なければ早期終了
    return text


def is_references_section(para_text: str) -> bool:
    """References セクションの開始を検出する。"""
    stripped = para_text.strip()
    return stripped in ("References", "# References", "References\n")


# ============================================================
# Declarations テキストの生成
# ============================================================

DECLARATIONS_TEXT = """Statements and Declarations

Funding
No funding was received to assist with the preparation of this manuscript.

Competing Interests
The authors have no relevant financial or non-financial interests to disclose.

Ethics Approval
This study used publicly available, anonymized, aggregate-level data from the National Database of Health Insurance Claims and Specific Health Checkups (NDB) Open Data, released by the Ministry of Health, Labour and Welfare of Japan. No individual-level data were accessed. Ethics committee approval was not required under Japanese regulations for secondary analysis of de-identified aggregate data.

Consent to Participate
Not applicable (no individual participants were enrolled).

Consent for Publication
Not applicable.

Data Availability
The NDB Open Data (Ministry of Health, Labour and Welfare of Japan) used in this study are publicly available at https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html. Digital elevation model data are available from the Geospatial Information Authority of Japan (https://www.gsi.go.jp/). Population Census data are available from e-Stat (https://www.e-stat.go.jp/). Analysis code is openly available at https://github.com/haruki00430/slope-walkability-diabetes-japan.

Authors' Contributions
Haruki Saito conceptualized the study, performed data acquisition and statistical analysis, created all visualizations, and wrote the manuscript. Tetsuya Ohira reviewed the manuscript and provided critical revisions. All authors read and approved the final manuscript.
Conceptualization: Haruki Saito; Methodology: Haruki Saito; Formal analysis and investigation: Haruki Saito; Writing — original draft preparation: Haruki Saito; Writing — review and editing: Haruki Saito, Tetsuya Ohira; Resources: Haruki Saito.
"""


# ============================================================
# メイン変換処理
# ============================================================

def convert_docx(input_path: Path, output_path: Path) -> None:
    """DOCX を JCH 形式に変換して保存する。"""

    if not input_path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_path}")

    print(f"入力: {input_path}")
    doc = Document(str(input_path))

    converted_count = 0
    in_references = False
    references_para_index = None

    # ---- Pass 1: 段落を走査し、引用変換 & References 位置を特定 ----
    for i, para in enumerate(doc.paragraphs):
        original_text = para.text

        # References セクション検出
        if is_references_section(original_text):
            in_references = True
            references_para_index = i
            print(f"  [INFO] References セクション検出: 段落 {i}")
            continue

        # References 以降は変換しない
        if in_references:
            continue

        # 引用変換（per-run: 書式を保持しつつ各 run のテキストを個別置換）
        new_text = convert_citations_in_text(original_text)
        if new_text != original_text:
            replace_text_in_para(para, original_text, new_text)
            converted_count += 1

    print(f"  [INFO] 引用変換: {converted_count} 箇所")

    # ---- Pass 2: Declarations セクションを References の前に挿入 ----
    if references_para_index is not None:
        insert_declarations_before_references(doc, references_para_index)
        print(f"  [INFO] Declarations セクションを挿入しました")
    else:
        print(f"  [WARNING] References セクションが見つかりませんでした。Declarations を末尾に追加します。")
        doc.add_paragraph()
        doc.add_heading("Statements and Declarations", level=1)
        for line in DECLARATIONS_TEXT.strip().split("\n"):
            doc.add_paragraph(line)

    # ---- 保存 ----
    doc.save(str(output_path))
    print(f"出力: {output_path}")
    print("変換完了。")


def replace_text_in_para(para, original_text: str, new_text: str) -> None:
    """
    段落内の各 run を個別に引用変換する（書式を完全保持）。

    各 run のテキストに convert_citations_in_text を直接適用する。
    run を結合しないため bold / italic / font size / color などが維持される。
    引用番号が複数 run にまたがる場合は変換不可だが、
    Vancouver 形式 n) は通常 1 run 内に完結するため実用上問題なし。
    """
    if not para.runs:
        return

    for run in para.runs:
        if not run.text:
            continue
        converted = convert_citations_in_text(run.text)
        if converted != run.text:
            run.text = converted


def insert_declarations_before_references(doc: Document, ref_para_index: int) -> None:
    """
    References セクションの直前に Declarations セクションを挿入する。
    python-docx は段落の「前に挿入」が難しいため、
    References 段落の XML 要素の前に新要素を挿入する。
    """
    from docx.oxml import OxmlElement
    from lxml import etree
    import copy

    ref_para = doc.paragraphs[ref_para_index]
    ref_elem = ref_para._element
    parent = ref_elem.getparent()

    # 空白段落
    blank_para = OxmlElement('w:p')
    parent.insert(list(parent).index(ref_elem), copy.deepcopy(blank_para))

    # Declarations のテキストを段落として挿入
    lines = DECLARATIONS_TEXT.strip().split("\n")
    for line in reversed(lines):
        new_para = OxmlElement('w:p')
        if line:
            run_elem = OxmlElement('w:r')
            text_elem = OxmlElement('w:t')
            text_elem.text = line
            text_elem.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            run_elem.append(text_elem)
            new_para.append(run_elem)
        idx = list(parent).index(ref_elem)
        parent.insert(idx, new_para)

    # "Statements and Declarations" 見出し
    heading_para = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), 'Heading1')
    pPr.append(pStyle)
    heading_para.append(pPr)
    run_elem = OxmlElement('w:r')
    text_elem = OxmlElement('w:t')
    text_elem.text = "Statements and Declarations"
    run_elem.append(text_elem)
    heading_para.append(run_elem)
    idx = list(parent).index(ref_elem)
    parent.insert(idx, heading_para)

    # 挿入前の空白
    blank_para2 = OxmlElement('w:p')
    idx = list(parent).index(ref_elem)
    parent.insert(idx, copy.deepcopy(blank_para2))


# ============================================================
# エントリポイント
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("JCH Format Converter")
    print("Vancouver 1) → JCH [1] 変換")
    print("=" * 60)
    print()

    # 出力ファイルが既に存在する場合の確認
    if OUTPUT_DOCX.exists():
        print(f"注意: {OUTPUT_DOCX.name} が既に存在します。上書きします。")

    convert_docx(INPUT_DOCX, OUTPUT_DOCX)

    print()
    print("=" * 60)
    print("次のステップ:")
    print("1. Manuscript_JCH.docx を Word で開いて内容を確認")
    print("2. Declarations セクションが References の前に挿入されているか確認")
    print("3. 引用番号が [1]〜[35] になっているか確認")
    print("4. References リストを APA-7 形式（Declarations_JCH.md）に手動で置き換え")
    print("5. 著者名・所属のプレースホルダーを実名に置き換え")
    print("6. Editorial Manager にアップロード")
    print("=" * 60)

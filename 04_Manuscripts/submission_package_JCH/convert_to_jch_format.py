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
# 例: 1)  → [1]
#     1), 2)  → [1, 2]
#     1)-3)   → [1-3]  (範囲表記は保持)
#     3), 4), 5) → [3-5] (連続は範囲に変換しない—原形保持)
CITATION_PATTERNS = [
    # 複合引用: "n), m), k)" → "[n, m, k]"
    (
        re.compile(r'(\d+)\),\s*(\d+)\),\s*(\d+)\)'),
        r'[\1, \2, \3]'
    ),
    # 複合引用: "n), m)" → "[n, m]"
    (
        re.compile(r'(\d+)\),\s*(\d+)\)'),
        r'[\1, \2]'
    ),
    # 範囲引用: "n)-m)" → "[n-m]"
    (
        re.compile(r'(\d+)\)-(\d+)\)'),
        r'[\1-\2]'
    ),
    # 単独引用: "n)" → "[n]"  ※ 文末の ")" は除外するため、直前が数字のみマッチ
    # ただし "Fig." "Table" "Eq." 等の後の括弧は除外
    (
        re.compile(r'(?<![A-Za-z\.\(])(\d{1,2})\)(?!\d)'),
        r'[\1]'
    ),
]


def convert_citations_in_text(text: str) -> str:
    """
    テキスト内のVancouver形式引用をJCH形式に変換する。
    References セクション以降のテキストは変換しない（呼び出し元で制御）。
    """
    for pattern, replacement in CITATION_PATTERNS:
        text = pattern.sub(replacement, text)
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
The NDB Open Data (Ministry of Health, Labour and Welfare of Japan) used in this study are publicly available at https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html. Digital elevation model data are available from the Geospatial Information Authority of Japan (https://www.gsi.go.jp/). Population Census data are available from e-Stat (https://www.e-stat.go.jp/). Analysis code is openly available at https://github.com/haruki00430/NDB_XXX_slope_diabetes.

Authors' Contributions
[Author 1] conceptualized the study, performed data acquisition and statistical analysis, created all visualizations, and wrote the manuscript. [Author 2] reviewed the manuscript and provided critical revisions. All authors read and approved the final manuscript.
Conceptualization: [Author 1]; Methodology: [Author 1]; Formal analysis and investigation: [Author 1]; Writing — original draft preparation: [Author 1]; Writing — review and editing: [Author 1], [Author 2]; Resources: [Author 1].
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

        # 引用変換
        new_text = convert_citations_in_text(original_text)
        if new_text != original_text:
            # 段落内の各 run を結合してから置換（書式を保持するため run ごとに処理）
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
    段落内のテキストを置換する。書式 (run) を保持するため、
    段落全体テキストで差分を検出し、変更箇所のみ run を更新する。

    簡易実装: 最初の run にすべてのテキストを集約し、書式を保持。
    ※ 複数 run にまたがる引用は先頭 run に集約される。
    """
    if not para.runs:
        return

    # 全 run のテキストを置換
    full_text = "".join(run.text for run in para.runs)
    new_full = convert_citations_in_text(full_text)

    if new_full == full_text:
        return

    # 最初の run に全テキストを設定、残りをクリア
    para.runs[0].text = new_full
    for run in para.runs[1:]:
        run.text = ""


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

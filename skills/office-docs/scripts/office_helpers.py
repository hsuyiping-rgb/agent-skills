"""Word / PowerPoint / Excel 共用小工具（重點：繁體中文字型不跑掉）。

用法（不必事先安裝套件）：
    uv run --with python-docx --with python-pptx --with openpyxl build.py
在 build.py 內：
    import sys; sys.path.insert(0, r"<本技能>/scripts")
    from office_helpers import *
"""
from __future__ import annotations

import sys
import unicodedata

# 預設字型：Windows 用微軟正黑體，macOS 用蘋方；公文類文件可改傳 "標楷體"
DEFAULT_CJK_FONT = "PingFang TC" if sys.platform == "darwin" else "Microsoft JhengHei"
DEFAULT_LATIN_FONT = "Arial"


# ───────────────────────── Word（python-docx） ─────────────────────────

def docx_new(cjk_font: str = DEFAULT_CJK_FONT, latin_font: str = DEFAULT_LATIN_FONT, size_pt: float = 12):
    """建立 A4 文件，並把內文與標題樣式的中英文字型都設好。"""
    from docx import Document
    from docx.shared import Cm, Pt

    doc = Document()
    for section in doc.sections:
        section.page_width, section.page_height = Cm(21), Cm(29.7)
        section.left_margin = section.right_margin = Cm(2.5)
        section.top_margin = section.bottom_margin = Cm(2.5)
    for name in ["Normal", "Title", "Heading 1", "Heading 2", "Heading 3", "List Bullet", "List Number"]:
        try:
            docx_set_style_font(doc.styles[name], cjk_font, latin_font)
        except KeyError:
            pass
    doc.styles["Normal"].font.size = Pt(size_pt)
    return doc


def docx_set_style_font(style, cjk_font: str, latin_font: str = DEFAULT_LATIN_FONT):
    """python-docx 的 font.name 只改英文字型；中文要另外寫 w:eastAsia。"""
    from docx.oxml.ns import qn

    style.font.name = latin_font
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), cjk_font)


def docx_add_table(doc, rows: list[list], header: bool = True, style: str = "Table Grid"):
    """rows[0] 為表頭；回傳 table。表頭自動加粗並設為跨頁重複。"""
    from docx.oxml.ns import qn

    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = style
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = "" if value is None else str(value)
            if header and r == 0:
                for run in cell.paragraphs[0].runs:
                    run.bold = True
    if header:
        trpr = table.rows[0]._tr.get_or_add_trPr()
        trpr.append(trpr.makeelement(qn("w:tblHeader"), {qn("w:val"): "true"}))
    return table


# ─────────────────────── PowerPoint（python-pptx） ───────────────────────

def pptx_new(widescreen: bool = True):
    """建立 16:9（預設）或 4:3 簡報。"""
    from pptx import Presentation
    from pptx.util import Inches

    prs = Presentation()
    if widescreen:
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    return prs


def pptx_set_run_font(run, cjk_font: str = DEFAULT_CJK_FONT, latin_font: str = DEFAULT_LATIN_FONT,
                      size_pt: float | None = None, bold: bool | None = None, color: str | None = None):
    """python-pptx 的 font.name 只改英文；中文要寫 <a:ea>。color 用 'RRGGBB'。"""
    from pptx.dml.color import RGBColor
    from pptx.oxml.ns import qn
    from pptx.util import Pt

    font = run.font
    font.name = latin_font
    if size_pt:
        font.size = Pt(size_pt)
    if bold is not None:
        font.bold = bold
    if color:
        font.color.rgb = RGBColor.from_string(color)
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {})
            rpr.append(el)
        el.set("typeface", cjk_font)


def pptx_add_text(slide, text: str | list[str], left, top, width, height, size_pt: float = 20,
                  bold: bool = False, color: str = "222222", cjk_font: str = DEFAULT_CJK_FONT,
                  bullets: bool = False):
    """在指定位置加文字框；text 給 list 會分段。尺寸請用 pptx.util.Inches/Cm。"""
    from pptx.util import Pt

    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    lines = [text] if isinstance(text, str) else text
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = p.add_run()
        run.text = ("• " if bullets else "") + line
        pptx_set_run_font(run, cjk_font, size_pt=size_pt, bold=bold, color=color)
        p.space_after = Pt(size_pt * 0.4)
    return box


def pptx_blank_slide(prs, bg_color: str | None = None):
    """加一張空白版面（layout 6），可選背景色。"""
    from pptx.dml.color import RGBColor

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    if bg_color:
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor.from_string(bg_color)
    return slide


# ─────────────────────────── Excel（openpyxl） ───────────────────────────

def _display_width(value) -> int:
    """中日韓全形字算 2 格，其餘算 1 格。"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in str(value))


def xlsx_write_table(ws, rows: list[list], start_row: int = 1, header_fill: str = "DCE6F1",
                     font_name: str = DEFAULT_CJK_FONT, freeze: bool = True, autofilter: bool = True):
    """把 rows（rows[0] 為表頭）寫進工作表：表頭底色＋粗體、細框線、凍結表頭、篩選、欄寬自動。"""
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    thin = Side(style="thin", color="BFBFBF")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for r, row in enumerate(rows):
        for c, value in enumerate(row, start=1):
            cell = ws.cell(row=start_row + r, column=c, value=value)
            cell.border = border
            cell.font = Font(name=font_name, bold=(r == 0))
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            if r == 0:
                cell.fill = PatternFill("solid", fgColor=header_fill)
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    xlsx_autofit(ws)
    last_col = get_column_letter(len(rows[0]))
    if freeze:
        ws.freeze_panes = ws.cell(row=start_row + 1, column=1)
    if autofilter:
        ws.auto_filter.ref = f"A{start_row}:{last_col}{start_row + len(rows) - 1}"


def xlsx_autofit(ws, min_width: int = 6, max_width: int = 60):
    """依內容（含中文全形寬度）調整欄寬；公式儲存格以公式長度估算。"""
    from openpyxl.utils import get_column_letter

    widths: dict[int, int] = {}
    for row in ws.iter_rows():
        for cell in row:
            if cell.value is not None:
                longest = max(_display_width(part) for part in str(cell.value).split("\n"))
                widths[cell.column] = max(widths.get(cell.column, 0), longest)
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = max(min_width, min(max_width, w + 2))

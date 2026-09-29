---
name: office-docs
description: 產生 Word（.docx）、PowerPoint（.pptx）、Excel（.xlsx）三種 Office 文件，繁體中文字型不跑掉，產出後轉圖目視檢查版面。當使用者說「做成 Word」「產生 Word 檔」「寫成 docx」「做一份 PPT」「做成投影片檔」「做 PowerPoint」「做成 Excel」「整理成試算表」「匯出 xlsx」「做成表格檔」，或要求把內容輸出成可下載、可編輯的 Office 檔案時，請使用此技能。Claude Code、Codex、Antigravity 通用；只需要 uv（套件由 uv 臨時載入，不必事先安裝）。
---

# Office 文件產生（Word／PowerPoint／Excel）

用 Python 腳本產生檔案：**腳本留在專案裡**，之後要改內容只要改腳本重跑，不必從頭再做。

## 工具

| 格式 | 套件 | 本技能的小工具（`scripts/office_helpers.py`） |
|------|------|---------------------------------------------|
| Word | python-docx | `docx_new()`（A4＋中英字型）、`docx_add_table()`（表頭跨頁重複） |
| PowerPoint | python-pptx | `pptx_new()`（16:9）、`pptx_blank_slide()`、`pptx_add_text()`、`pptx_set_run_font()` |
| Excel | openpyxl | `xlsx_write_table()`（表頭樣式、框線、凍結、篩選、欄寬）、`xlsx_autofit()`（中文寬度） |

執行方式（不需 pip install）：

```bash
uv run --with python-docx --with python-pptx --with openpyxl build_xxx.py
```

腳本開頭引入小工具（路徑換成本技能實際位置，如 `~/.claude/skills/office-docs/scripts`）：

```python
import sys; sys.path.insert(0, r"<本技能>/scripts")
from office_helpers import *
```

沒有 uv 時才改用 `pip install python-docx python-pptx openpyxl`（Windows 用 `py -m pip`）。

## 工作流程

1. **確認需求**：用途與讀者、頁數／張數、要不要沿用既有範本檔（有範本就以範本開啟再填，保留原樣式）。內容不明確時先列大綱給使用者確認。
2. **寫建置腳本**：存成專案內 `build_<檔名>.py`；輸出檔放專案的 `output/`（或使用者指定位置），檔名用中文描述性名稱。
3. **執行腳本**產生檔案。
4. **轉圖檢查**（有 LibreOffice 時必做）：
   ```bash
   uv run --with pymupdf <本技能>/scripts/render_preview.py <檔案> --dpi 80
   ```
   會在檔案旁產生 `<檔名>_<副檔名>_preview/page-XX.png`；**逐頁看圖**確認：中文沒變方框、文字沒溢出、表格沒被切斷、投影片沒擠爆。有問題改腳本重跑。
   沒有 LibreOffice → 說明無法目視檢查，改用程式讀回檔案核對文字與結構。
5. **交付**：回報檔案路徑、頁數／張數／工作表、檢查結果；預覽資料夾是暫存，交付後可刪。

## Word 要點

- 中文字型要寫 `w:eastAsia`（`docx_new()` 已處理）；只設 `font.name` 中文會變新細明體。
- 公文、正式文件常用字型：`docx_new(cjk_font="標楷體")`；一般文件用微軟正黑體（預設）。
- 標題用 `doc.add_heading(text, level=1..3)`，才會出現在 Word 導覽窗格與目錄。
- 分頁：`doc.add_page_break()`；頁首頁尾：`doc.sections[0].header.paragraphs[0].text = "..."`。
- 圖片：`doc.add_picture(path, width=Cm(15))`，寬度不要超過版心（A4 左右邊界 2.5 cm → 16 cm）。

## PowerPoint 要點

- 預設 16:9（13.333 × 7.5 吋）。用空白版面＋自己擺文字框，比套內建版面好控制。
- 中文字型要寫 `<a:ea>`（`pptx_set_run_font()` 已處理），否則換電腦開會變字。
- 版面原則：一張一個重點；標題 36–44 pt、內文 20–28 pt；內文不超過 6 行，塞不下就拆頁。
- 左右邊界至少 0.5 吋；文字框寬 × 字數要算過，轉圖檢查有無溢出。
- 講者備忘稿：`slide.notes_slide.notes_text_frame.text = "..."`。
- 圖片：`slide.shapes.add_picture(path, left, top, width=...)`，只給寬或高其一以保持比例。

## Excel 要點

- 一張工作表一種資料；第一列是表頭，`xlsx_write_table()` 會凍結表頭並加篩選。
- **能用公式就用公式**（`ws["D2"] = "=B2*C2"`），讓使用者改數字時會自動重算，不要把算好的結果寫死。
- 數字存成數字、日期存成 `datetime`，不要存成文字；格式用 `cell.number_format = "#,##0"`、`"yyyy/mm/dd"`、`"0.0%"`。
- 中文欄寬要以全形 2 格計算（`xlsx_autofit()` 已處理）。
- 讀既有檔要保留公式：`load_workbook(path)`；只要看計算結果才加 `data_only=True`（此模式存檔會把公式弄丟）。

## 不該做的事

- ❌ 沒轉圖檢查就說「完成了」（有 LibreOffice 時）
- ❌ 覆蓋使用者既有的 Office 檔；要改就另存新檔或先備份
- ❌ 把學生個資放進要分享的檔案；範例用代號或匿名

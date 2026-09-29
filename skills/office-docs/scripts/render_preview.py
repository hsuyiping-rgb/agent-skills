"""把 .docx / .pptx / .xlsx 轉成 PDF，再把每頁轉成 PNG，供 Agent 目視檢查版面。

用法：
    uv run --with pymupdf render_preview.py <檔案> [輸出資料夾] [--dpi 80]
需要 LibreOffice（soffice）。找不到時會說明並以結束碼 2 離開。
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANDIDATES = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


def find_soffice() -> str | None:
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    return next((p for p in CANDIDATES if os.path.exists(p)), None)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("outdir", nargs="?")
    ap.add_argument("--dpi", type=int, default=80)
    args = ap.parse_args()

    src = Path(args.file).resolve()
    outdir = Path(args.outdir or src.parent / f"{src.stem}_{src.suffix.lstrip('.')}_preview").resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    soffice = find_soffice()
    if not soffice:
        print("找不到 LibreOffice（soffice）。請安裝後再預覽：winget install TheDocumentFoundation.LibreOffice／brew install --cask libreoffice")
        return 2

    if src.suffix.lower() == ".pdf":
        pdf = src
    else:
        # 獨立設定檔目錄，避免與使用者開著的 LibreOffice 衝突
        with tempfile.TemporaryDirectory() as profile:
            subprocess.run(
                [soffice, f"-env:UserInstallation={Path(profile).as_uri()}", "--headless",
                 "--convert-to", "pdf", "--outdir", str(outdir), str(src)],
                # 不接管 stdout/stderr：Windows 上 soffice.bin 會繼承管線，導致永遠等不到 EOF
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180,
            )
        pdf = outdir / f"{src.stem}.pdf"
        if not pdf.exists():
            print("PDF 轉檔失敗")
            return 1

    import fitz  # pymupdf

    with fitz.open(pdf) as d:
        for i, page in enumerate(d, start=1):
            out = outdir / f"page-{i:02d}.png"
            page.get_pixmap(dpi=args.dpi).save(out)
            print(out)
        print(f"共 {d.page_count} 頁；PDF：{pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

---
name: PDF Reading Workaround (Windows)
description: Poppler is installed; Read tool can't use it directly — convert to PNG first, then Read
type: reference
originSessionId: d77fc6bd-119f-4192-b2c8-a8592257d2b6
---
Poppler is installed at `C:\Users\dj\poppler\poppler-24.08.0\Library\bin\pdftoppm`.

The Read tool cannot read PDFs directly on this machine (pdftoppm not in its PATH). Workaround: convert the PDF to PNG images using Bash, then Read the PNG.

**How to apply — use this exact pattern every time you need to read a PDF:**

```bash
"/c/Users/dj/poppler/poppler-24.08.0/Library/bin/pdftoppm" -png -r 150 -f 1 -l 2 "/c/path/to/file.pdf" "/c/Users/dj/tmp_pdf_page" && ls /c/Users/dj/tmp_pdf_page*
```

Then Read each PNG (e.g. `/c/Users/dj/tmp_pdf_page-01.png`), then delete temp files when done:

```bash
rm /c/Users/dj/tmp_pdf_page-*.png
```

**Notes:**
- `-f 1 -l 2` = pages 1 through 2. Adjust range as needed.
- Font warnings ("No display font for Symbol") are harmless — images still render correctly.
- Always clean up temp PNGs after reading.
- Installed 2026-04-15 via manual zip download (no admin rights needed).

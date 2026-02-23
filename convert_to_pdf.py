"""
Convert Markdown to PDF using Chrome headless
"""
import markdown
import subprocess
import tempfile
import os

# Paths
md_file = r"c:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\3_Documentation\BUSINESS_OVERVIEW_For_Partners.md"
pdf_file = r"c:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\3_Documentation\Business Overview Test.pdf"

# Read markdown
print("Reading Markdown file...")
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Convert to HTML with styling
print("Converting Markdown to HTML...")
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @page {{
            size: letter;
            margin: 0.75in;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            font-size: 24pt;
            page-break-after: avoid;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
            margin-top: 30px;
            font-size: 18pt;
            page-break-after: avoid;
        }}
        h3 {{
            color: #7f8c8d;
            font-size: 14pt;
            page-break-after: avoid;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
            font-size: 10pt;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #555;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        ul, ol {{
            margin: 10px 0;
        }}
    </style>
</head>
<body>
{markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'nl2br'])}
</body>
</html>
"""

# Save to temp HTML file
temp_html = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
temp_html.write(html_content)
temp_html.close()

try:
    # Try to use Chrome to print to PDF
    print("Converting HTML to PDF using Chrome...")
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break
    
    if chrome_path:
        cmd = [
            chrome_path,
            '--headless',
            '--disable-gpu',
            '--print-to-pdf=' + pdf_file,
            temp_html.name
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"[OK] PDF created: {pdf_file}")
    else:
        print("❌ Chrome not found. PDF file was not created.")
        print(f"📄 HTML file saved to: {temp_html.name}")
        print("You can:")
        print("  1. Open the HTML file in your browser")
        print("  2. Press Ctrl+P")
        print("  3. Select 'Save as PDF'")
finally:
    # Clean up temp file
    try:
        os.unlink(temp_html.name)
    except:
        pass

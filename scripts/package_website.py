#!/usr/bin/env python3
"""Build a portable single-file prototype and editable source ZIP."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT = Path(__file__).resolve().parents[1]
site = ROOT / 'Website'
output = ROOT / 'output'
output.mkdir(exist_ok=True)
html = (site / 'index.html').read_text()
html = html.replace('<link rel="stylesheet" href="styles.css">', '<style>\n' + (site/'styles.css').read_text() + '\n</style>')
html = html.replace('<script defer src="config.js"></script><script defer src="app.js"></script>', '')
html = html.replace('</body>', '<script>\n' + (site/'config.js').read_text() + '\n' + (site/'app.js').read_text() + '\n</script></body>')
portable = output / 'tech2go-prototype.html'
portable.write_text(html)
with ZipFile(output/'tech2go-website.zip','w',ZIP_DEFLATED) as archive:
    archive.write(portable, portable.name)
    for file in sorted(site.iterdir()):
        if file.is_file():
            archive.write(file, 'Website/' + file.name)
print(portable)
print(output/'tech2go-website.zip')

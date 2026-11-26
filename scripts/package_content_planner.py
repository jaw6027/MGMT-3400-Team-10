#!/usr/bin/env python3
"""Regenerate starter data and bundle the offline content planner."""
import csv
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
site=ROOT/'content_planner'
with (site/'content_plan.csv').open(newline='') as f:
    rows=list(csv.DictReader(f))
# Escape less-than so edited content cannot terminate a script element.
seed='window.TECH2GO_CONTENT_SEED = '+json.dumps(rows,ensure_ascii=True).replace('<','\\u003c')+';\n'
(site/'seed.js').write_text(seed)
html=(site/'index.html').read_text()
html=html.replace('<link rel="stylesheet" href="styles.css">','<style>\n'+(site/'styles.css').read_text()+'\n</style>')
html=html.replace('<script defer src="seed.js"></script><script defer src="app.js"></script>','')
html=html.replace('</body>','<script>\n'+seed+'\n'+(site/'app.js').read_text()+'\n</script></body>')
output=ROOT/'output';output.mkdir(exist_ok=True)
portable=output/'tech2go-content-planner.html';portable.write_text(html)
with ZipFile(output/'tech2go-content-planner.zip','w',ZIP_DEFLATED) as z:
    z.write(portable,portable.name)
    for file in sorted(site.iterdir()):
        if file.is_file():z.write(file,'content_planner/'+file.name)
print(f'Built {len(rows)} starter stories: {portable}')

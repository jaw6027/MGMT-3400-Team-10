#!/usr/bin/env python3
"""Check that sourced catalog, price list and distributed SQLite snapshot agree."""
import csv
import sqlite3
import sys
import tempfile
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from database import ROOT, TABLES, connect, initialize


def records(db, table):
    return db.execute(f'SELECT * FROM {table} ORDER BY 1,2').fetchall()

with tempfile.TemporaryDirectory() as temp:
    rebuilt = Path(temp)/'rebuilt.sqlite3'
    initialize(rebuilt)
    with connect(rebuilt) as db:
        original={t:records(db,t) for t in TABLES}
    initialize(rebuilt)
    with connect(rebuilt) as db, connect(ROOT/'database/retailers.sqlite3') as snapshot:
        for table in TABLES:
            assert records(db,table)==original[table], f'Reimport changed {table}'
            assert records(snapshot,table)==original[table], f'Snapshot differs: {table}'
        for connection in (db,snapshot):
            assert connection.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
            assert not connection.execute('PRAGMA foreign_key_check').fetchall()
        text=(ROOT/'common_parts_prices.txt').read_text()
        rows=db.execute('''SELECT p.id,p.part_type,l.unit_price_cents,l.currency,l.checked_at,
                                  l.shipping_cents,l.tax_cents,l.product_url
                           FROM parts p JOIN supplier_listings l ON l.part_id=p.id''').fetchall()
        assert len(rows)==22
        groups=Counter()
        for ident,label,cents,currency,checked,shipping,tax,url in rows:
            assert text.count(f'Part ID {ident} |')==1
            assert f'Part ID {ident} | {label.split(" - ",1)[1]} | USD ${cents/100:.2f}' in text
            assert currency=='USD' and isinstance(cents,int) and cents>0
            assert checked=='2026-11-26' and shipping is None and tax is None
            assert url in text
            groups[label.split(' - ',1)[0]]+=1
        assert groups=={'Cellphone':6,'Laptop':8,'Desktop':8}
        assert db.execute('SELECT COUNT(*) FROM parts').fetchone()[0]==len(rows)
        assert db.execute("SELECT COUNT(*) FROM listing_comparison WHERE cost_status='incomplete' AND landed_total_cents IS NULL").fetchone()[0]==22
        assert db.execute("SELECT COUNT(*) FROM supplier_listings WHERE stock_status='out_of_stock'").fetchone()[0]==3
        assert db.execute('SELECT COUNT(*) FROM purchases').fetchone()[0]==0
        assert db.execute('SELECT COUNT(*) FROM purchase_items').fetchone()[0]==0
print('PASS: 22 products/listings (6 cellphone, 8 laptop, 8 desktop).')
print('PASS: Every text price, product ID and URL matches the catalog; cents and dates valid.')
print('PASS: Tracked SQLite snapshot matches all six source CSV tables and repeat imports.')
print('PASS: integrity_check=ok; foreign_key_check=[]; unknown costs stay incomplete.')
print('PASS: Three out-of-stock references labeled; no fabricated purchases.')

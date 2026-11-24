#!/usr/bin/env python3
"""Integration validation; all synthetic records live in a temporary DB."""
import csv
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from database import ROOT, TABLES, connect, initialize

checks = []
def passed(message):
    checks.append(message)
    print('PASS:', message)

def rejected(db, sql, params=()):
    try:
        db.execute(sql, params)
    except sqlite3.IntegrityError:
        return
    raise AssertionError(f'Invalid data accepted: {sql}')

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / 'validation.sqlite3'
    with (ROOT/'data/suppliers.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len({r['website'] for r in rows}) == 9
    assert all(r['verification_status']=='unverified' and not r['last_verified_at'] for r in rows)
    passed('CSV contains nine unique unverified leads with no verification dates')
    initialize(path)
    with connect(path) as db:
        assert db.execute('PRAGMA foreign_keys').fetchone()[0] == 1
        assert set(TABLES) <= {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        counts = {t:db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in TABLES}
        assert counts == dict(suppliers=9, supplier_categories=11, parts=0, supplier_listings=0, purchases=0, purchase_items=0)
        db.execute("UPDATE suppliers SET notes='Manually edited detail' WHERE id=1")
    passed('Six required tables, enabled foreign keys, nine suppliers and eleven category links')
    initialize(path)
    with connect(path) as db:
        assert counts == {t:db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in TABLES}
        assert db.execute('SELECT notes FROM suppliers WHERE id=1').fetchone()[0]=='Manually edited detail'
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
        assert dict(db.execute('SELECT device_category, COUNT(*) FROM supplier_categories GROUP BY device_category')) == {'computers':5,'game consoles':2,'mobile devices':4}
    passed('Second import adds no duplicates and preserves manually edited supplier details')
    passed('Integrity and foreign key checks pass; category filtering returns 5 computer, 2 console and 4 mobile leads')
    result = subprocess.check_output([sys.executable,'-c', 'import sqlite3,sys; d=sqlite3.connect(sys.argv[1]); print(d.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0]); print(d.execute("SELECT notes FROM suppliers WHERE id=1").fetchone()[0])',str(path)],text=True)
    assert result.splitlines()==['9','Manually edited detail']
    passed('Separate Python process reopens persisted suppliers and manual edit')
    # Synthetic records only. Roll back on completion.
    with connect(path) as db:
        db.execute('BEGIN')
        db.execute("INSERT INTO parts VALUES (1,'mobile devices','SYNTHETIC','TEST MODEL A','screen','new','test')")
        db.execute("INSERT INTO parts VALUES (2,'mobile devices','SYNTHETIC','TEST MODEL B','screen','new','test')")
        insert = '''INSERT INTO supplier_listings
        (id,supplier_id,part_id,actual_seller,product_url,unit_price_cents,currency,shipping_cents,tax_cents,minimum_order_quantity,checked_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)'''
        for ident, supplier, part, price, ship, tax in [(1,1,1,1000,200,100),(2,2,1,900,None,100),(3,3,2,1,0,0)]:
            db.execute(insert,(ident,supplier,part,'SYNTHETIC','https://example.invalid/test',price,'USD',ship,tax,1,'2026-11-23'))
        comparison = 'SELECT supplier_name,' + (ROOT/'sql/queries.sql').read_text().split('SELECT supplier_name,', 1)[1].split(';', 1)[0]
        # Use the actual documented comparison query, including its bound filters.
        results = db.execute(comparison,{'part_id':1,'currency':'USD'}).fetchall()
        assert len(results)==2
        assert results[0][0]=='MobileSentrix' and results[0][7:9]==(1300,'complete')
        assert results[1][7:9]==(None,'incomplete')
        passed('Documented comparison isolates exact part/currency and puts unknown totals last')
        rejected(db,"INSERT INTO supplier_categories VALUES (999,'computers')")
        rejected(db,"INSERT INTO supplier_categories VALUES (1,'invalid')")
        rejected(db,"INSERT INTO supplier_categories VALUES (1,'mobile devices')")
        rejected(db,"UPDATE supplier_listings SET unit_price_cents=-1 WHERE id=1")
        rejected(db,"UPDATE supplier_listings SET shipping_cents=1.5 WHERE id=1")
        rejected(db,"UPDATE supplier_listings SET minimum_order_quantity=0 WHERE id=1")
        db.execute("INSERT INTO purchases (id,supplier_id,order_reference,order_date,currency) VALUES (1,1,'SYNTHETIC','2026-11-23','USD')")
        db.execute("INSERT INTO purchase_items (purchase_id,part_id,supplier_id,listing_id,quantity) VALUES (1,1,1,1,2)")
        rejected(db,"UPDATE purchase_items SET quantity=0")
        rejected(db,"UPDATE purchase_items SET defective_quantity=3")
        rejected(db,"UPDATE purchase_items SET listing_id=2")
        rejected(db,"UPDATE purchase_items SET part_id=2")
        rejected(db,"UPDATE purchases SET total_cents=-1")
        db.rollback()
        assert db.execute('SELECT COUNT(*) FROM parts').fetchone()[0]==0
    passed('Constraints reject orphan keys, duplicate categories, invalid categories/costs/quantities and mismatched purchase listings')
    # Explicit CSV updates work; failed imports roll back all data changes.
    csvdir=Path(tmp)/'csv'; shutil.copytree(ROOT/'data',csvdir)
    rows[0]['notes']='Explicit CSV update'
    with (csvdir/'suppliers.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    initialize(path,csvdir,True)
    with connect(path) as db:
        assert db.execute('SELECT notes FROM suppliers WHERE id=1').fetchone()[0]=='Explicit CSV update'
    rows[0]['notes']='Must roll back'
    with (csvdir/'suppliers.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    with (csvdir/'supplier_categories.csv').open('a') as f: f.write('999,computers\n')
    try:
        initialize(path,csvdir,True)
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError('Invalid CSV import accepted')
    with connect(path) as db:
        assert db.execute('SELECT notes FROM suppliers WHERE id=1').fetchone()[0]=='Explicit CSV update'
    passed('Explicit CSV updates apply; invalid imports roll back without partial data edits')
print(f'All {len(checks)} validation groups passed. Synthetic records removed with temporary database.')

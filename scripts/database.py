#!/usr/bin/env python3
"""Initialize/import editable CSVs, preserving existing records by default."""
import argparse
import csv
import datetime
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ('suppliers', 'supplier_categories', 'parts', 'supplier_listings', 'purchases', 'purchase_items')
KEYS = {'supplier_categories': ('supplier_id', 'device_category'), 'purchase_items': ('purchase_id', 'part_id')}
INTEGER_FIELDS = {'id', 'supplier_id', 'part_id', 'purchase_id', 'listing_id', 'quantity',
                  'defective_quantity', 'minimum_order_quantity', 'unit_price_cents',
                  'shipping_cents', 'tax_cents', 'total_cents'}
DATE_FIELDS = {'last_verified_at', 'checked_at', 'order_date', 'arrival_date'}

def connect(path):
    db = sqlite3.connect(path)
    db.execute('PRAGMA foreign_keys=ON')
    assert db.execute('PRAGMA foreign_keys').fetchone()[0] == 1
    return db

def initialize(path, csv_dir=ROOT / 'data', update_existing=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.executescript((ROOT / 'sql/schema.sql').read_text())
        for table in TABLES:
            columns = [row[1] for row in db.execute(f'PRAGMA table_info({table})')]
            keys = KEYS.get(table, ('id',))
            with (Path(csv_dir) / f'{table}.csv').open(newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                if reader.fieldnames != columns:
                    raise ValueError(f'{table}: CSV headers must be {columns}')
                seen = set()
                for line, row in enumerate(reader, 2):
                    if None in row or any(v is None for v in row.values()):
                        raise ValueError(f'{table}:{line}: incorrect field count')
                    values = {k: v.strip() or None for k, v in row.items()}
                    for k, v in values.items():
                        if v is not None and k in INTEGER_FIELDS:
                            values[k] = int(v)
                        if v is not None and k in DATE_FIELDS:
                            datetime.date.fromisoformat(v)
                    key = tuple(values[k] for k in keys)
                    if key in seen:
                        raise ValueError(f'{table}:{line}: duplicate key {key}')
                    seen.add(key)
                    cols = ','.join(columns)
                    binds = ','.join('?' for _ in columns)
                    conflict = ','.join(keys)
                    action = 'DO NOTHING'
                    if update_existing and any(c not in keys for c in columns):
                        action = 'DO UPDATE SET ' + ','.join(f'{c}=excluded.{c}' for c in columns if c not in keys)
                    db.execute(f'INSERT INTO {table} ({cols}) VALUES ({binds}) ON CONFLICT({conflict}) {action}',
                               [values[c] for c in columns])
        if db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Foreign key validation failed')
    return path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=ROOT / 'output/retailers.sqlite3')
    parser.add_argument('--csv-dir', type=Path, default=ROOT / 'data')
    parser.add_argument('--update-existing', action='store_true', help='Explicitly apply CSV values, including blanks, to existing rows; back up DB first')
    args = parser.parse_args()
    initialize(args.db, args.csv_dir, args.update_existing)
    with connect(args.db) as db:
        print(f'Database: {args.db.resolve()}')
        for table in TABLES:
            print(f'{table}: {db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]}')
        print('integrity_check:', db.execute('PRAGMA integrity_check').fetchone()[0])
        print('foreign_key_check:', db.execute('PRAGMA foreign_key_check').fetchall())

if __name__ == '__main__':
    main()

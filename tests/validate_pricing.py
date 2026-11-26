#!/usr/bin/env python3
"""Independent arithmetic and recipe checks for the proposed service pricing model."""
import csv
import json
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from price_repairs import ROOT, calculate, build

settings=json.loads((ROOT/'pricing/assumptions.json').read_text())
# Hand-calculated examples: $50 merchandise -> $65 parts charge + $95 labor
# + $15 overhead = $175. $175 / .95 = $184.2105..., rounded upward -> $185.
result=calculate(Decimal('50'),Decimal('1'),'repair',settings)
assert result['planning_price']==Decimal('185.00')
assert result['reserve']==Decimal('9.25')
assert result['contribution']==Decimal('65.75')  # 185 - 50 - 45 - 15 - 9.25
# Minimum labor and product-only behavior must differ.
assert calculate('0','0.1','repair',settings)['labor_charge']==Decimal('47.50')
product=calculate('24.95','0','product',settings)
assert product['planning_price']==Decimal('35.00')
assert product['labor_charge']==0 and product['overhead']==0
for reserve in ('100','101'):
    bad=dict(settings,rework_reserve_percent_of_revenue=reserve)
    try: calculate('1','1','repair',bad)
    except ValueError: pass
    else: raise AssertionError('Invalid reserve accepted')
for value in ('-1','NaN','Infinity'):
    try: calculate(value,'1','repair',settings)
    except ValueError: pass
    else: raise AssertionError('Invalid amount accepted')
with tempfile.TemporaryDirectory() as temp:
    rows=build(Path(temp));byid={r['service_id']:r for r in rows}
    assert len(rows)==26 and len(byid)==26
    with (ROOT/'data/parts.csv').open(newline='') as f:
        ids={r['id'] for r in csv.DictReader(f)}
    assert {r['primary_part_id'] for r in rows}==ids
    assert Decimal(byid['S101']['planning_price_usd'])==210
    assert Decimal(byid['S102']['planning_price_usd'])==165
    assert Decimal(byid['S122']['catalog_parts_cost_usd'])==Decimal('2.00')
    assert Decimal(byid['S123']['catalog_parts_cost_usd'])==Decimal('74.98')
    assert Decimal(byid['S123']['planning_price_usd'])==320
    assert Decimal(byid['S125']['planning_price_usd'])==420
    assert all('planning_only' in r['price_status'] and 'freight/tax unquoted' in r['price_status'] for r in rows)
    assert {r['service_id'] for r in rows if 'out of stock' in r['price_status']}=={'S117','S118','S120'}
    for row in rows:
        price=Decimal(row['planning_price_usd']);reserve=Decimal(row['reserve_usd'])
        assert price % 5==0
        assert price-reserve>=Decimal(row['parts_charge_usd'])+Decimal(row['labor_charge_usd'])+Decimal(row['overhead_usd'])
    for name in ('repair_prices.csv','pricing_model.txt'):
        assert (Path(temp)/name).read_bytes()==(ROOT/'pricing'/name).read_bytes(),f'Regenerate stale {name}'
print('PASS: independent price/reserve/contribution calculations; minimum labor; product-only sale.')
print('PASS: all 26 catalog items covered; kits, fractional packs and shared consumables priced.')
print('PASS: out-of-stock and unknown freight/tax preserved as planning warnings.')
print('PASS: negative/non-finite inputs and invalid reserve rates rejected; generated files reproducible.')

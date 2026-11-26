#!/usr/bin/env python3
"""Generate indicative service prices from dated supplier listings and editable assumptions."""
import argparse
import csv
import json
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENT = Decimal('0.01')

def money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)

def amount(value):
    result=Decimal(str(value))
    if not result.is_finite() or result<0:
        raise ValueError(f'Expected finite nonnegative amount: {value}')
    return result

def read_csv(path):
    with path.open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def calculate(parts_cost, hours, job_type, settings):
    """No supplier freight/tax is imputed. This is a merchandise-only planning scenario."""
    parts_cost, hours=amount(parts_cost),amount(hours)
    if job_type not in ('repair','product'):
        raise ValueError(f'Unknown job type: {job_type}')
    billed=max(hours,amount(settings['minimum_service_hours'])) if job_type=='repair' else hours
    labor=money(billed*amount(settings['labor_rate_per_hour']))
    parts_charge=money(parts_cost*(1+amount(settings['parts_markup_percent'])/100))
    overhead=amount(settings['service_overhead_per_job']) if job_type=='repair' else Decimal(0)
    reserve_rate=amount(settings['rework_reserve_percent_of_revenue'])/100
    step=amount(settings['round_up_to_dollars'])
    if reserve_rate>=1 or step==0:
        raise ValueError('Reserve must be less than 100%; rounding step must be positive')
    raw=(parts_charge+labor+overhead)/(1-reserve_rate)
    price=money((raw/step).to_integral_value(rounding=ROUND_CEILING)*step)
    tech_cost=money(billed*amount(settings['loaded_technician_cost_per_hour']))
    reserve=money(price*reserve_rate)
    return dict(parts_charge=parts_charge,billed_hours=billed,labor_charge=labor,
                overhead=money(overhead),planning_price=price,technician_cost=tech_cost,
                reserve=reserve,contribution=money(price-parts_cost-tech_cost-overhead-reserve))

def build(output_dir):
    settings=json.loads((ROOT/'pricing/assumptions.json').read_text())
    if settings['currency']!='USD':
        raise ValueError('Catalog pricing currently requires USD')
    parts={r['id']:r for r in read_csv(ROOT/'data/parts.csv')}
    listings={}
    for listing in read_csv(ROOT/'data/supplier_listings.csv'):
        if listing['part_id'] in listings:
            raise ValueError('Multiple offers per part: select an offer explicitly before pricing')
        listings[listing['part_id']]=listing
    services=read_csv(ROOT/'pricing/services.csv')
    seen=set();results=[]
    for service in services:
        if service['service_id'] in seen:
            raise ValueError('Duplicate service ID')
        seen.add(service['service_id'])
        if service['primary_part_id'] not in parts:
            raise ValueError('Primary part not in catalog')
        cost=Decimal(0);component_ids=[];flags=[];basis=[];dates=[]
        for component in service['components'].split(';'):
            ident,quantity=component.split(':');quantity=amount(quantity)
            if quantity<=0 or ident in component_ids:
                raise ValueError('Component quantities must be positive and IDs unique')
            part=parts[ident];offer=listings[ident];component_ids.append(ident)
            if offer['currency']!='USD' or not offer['unit_price_cents']:
                raise ValueError('Every component needs an explicit USD price')
            cost+=amount(offer['unit_price_cents'])/100*quantity
            basis.append(f'{ident} x {quantity} @ ${Decimal(offer["unit_price_cents"])/100:.2f}')
            dates.append(offer['checked_at'])
            if offer['stock_status']=='out_of_stock':flags.append(f'part {ident} out of stock')
            if not part['condition']:flags.append(f'part {ident} condition unknown')
            if part['condition'] in ('used','refurbished'):flags.append(f'part {ident} {part["condition"]}')
        if service['primary_part_id'] not in component_ids:
            raise ValueError('Recipe must include primary part')
        # Missing freight/tax remain visible; these prices never become confirmed quotes.
        cost=money(cost)
        calculated=calculate(cost,service['labor_hours'],service['job_type'],settings)
        result=dict(service_id=service['service_id'],primary_part_id=service['primary_part_id'],
                    service_name=service['service_name'],job_type=service['job_type'],
                    components=service['components'],catalog_parts_cost_usd=f'{cost:.2f}',
                    labor_hours=service['labor_hours'],
                    **{k+'_usd' if k!='billed_hours' else k:str(v) for k,v in calculated.items()},
                    price_status='planning_only; freight/tax unquoted'+(';'+';'.join(flags) if flags else ''),
                    source_price_dates=';'.join(sorted(set(dates))),cost_basis='; '.join(basis),scope_notes=service['scope_notes'])
        results.append(result)
    output_dir.mkdir(parents=True,exist_ok=True)
    with (output_dir/'repair_prices.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=results[0].keys(),lineterminator='\n');writer.writeheader();writer.writerows(results)
    notes=[
      'TECH 2 GO - REPAIR PRICING MODEL',f'Model date: {settings["model_date"]} | USD | Business-planning assumptions',
      '', 'This model uses the existing dated parts catalog. It is not a competitor survey',
      'or a guarantee of actual repair time, margin, availability or final customer price.',
      'No new supplier prices were researched. Product source links and model compatibility',
      'are in common_parts_prices.txt and data/supplier_listings.csv.',
      '', 'EDITABLE ASSUMPTIONS',
      f'Labor selling rate: ${amount(settings["labor_rate_per_hour"]):.2f}/hour.',
      f'Minimum repair labor: {settings["minimum_service_hours"]} hours. Product-only sales have no labor minimum.',
      f'Parts markup: {settings["parts_markup_percent"]}% above allocated catalog cost ({amount(settings["parts_markup_percent"])/(100+amount(settings["parts_markup_percent"]))*100:.2f}% margin on that parts charge).',
      f'Per-repair overhead allowance: ${amount(settings["service_overhead_per_job"]):.2f}; product-only sale allowance: $0.',
      f'Rework/warranty reserve: {settings["rework_reserve_percent_of_revenue"]}% of modeled pretax revenue.',
      f'Round customer planning prices UP to the next ${amount(settings["round_up_to_dollars"]):.2f}.',
      f'Loaded technician cost for contribution analysis: ${amount(settings["loaded_technician_cost_per_hour"]):.2f}/billed hour.',
      'All rates and times are proposed assumptions; replace them with measured business costs.',
      '', 'FORMULA',
      'P = allocated catalog merchandise cost of the recipe (parts, kits, packs, consumables).',
      'B = P x (1 + markup) + billable hours x labor rate + per-job overhead.',
      'Planning price = round UP [ B / (1 - reserve rate) ] to the rounding increment.',
      'Component cost and parts/labor charges are rounded to cents before final rounding.',
      'Contribution = price - P - assumed technician cost - overhead allowance - reserve.',
      'This contribution is NOT net profit. It excludes unknown sourcing costs, payment fees,',
      'taxes, travel, idle time and fixed costs not covered by the per-job overhead allowance.',
      'The hourly labor rate is selling revenue, not a second cash labor expense.',
      '', 'DIAGNOSTICS AND QUOTING',
      f'Proposed diagnostic fee: ${amount(settings["diagnostic_fee"]):.2f} for up to {settings["diagnostic_hours"]} hours of initial assessment.',
      'For completed repairs, credit that fee against the full modeled price; do not add it.',
      'Balance due = approved repair total minus diagnostic deposit already paid, plus any agreed extra costs/tax.',
      'If the customer declines repair, the proposed charge is the diagnostic fee only.',
      'Time beyond the initial assessment requires an agreed quote. This is a proposed',
      'business policy, not an existing customer agreement. Routine diagnosis/testing are',
      'included in the service-hour assumptions; do not charge for the same time twice.',
      '', 'PLANNING PRICES BY SERVICE',
      'All prices below EXCLUDE unquoted supplier shipping, sourcing taxes, customer sales',
      'tax if applicable, travel and unlisted additional work. Missing costs are not known zero.',
      'Baseline scenario uses merchandise costs only. Confirm delivered procurement costs',
      'before issuing a quote; replace P with actual landed cost where appropriate and',
      'avoid counting recoverable taxes or separately billed freight twice.',
      '']
    for group in ('Cellphone','Laptop','Desktop'):
        notes += [group.upper(),'--------------------']
        for result in results:
            if not parts[result['primary_part_id']]['part_type'].startswith(group+' - '):continue
            notes += [f'{result["service_id"]} | {result["service_name"]} | Planning price ${Decimal(result["planning_price_usd"]):.2f}',
                      f'  Parts: ${Decimal(result["catalog_parts_cost_usd"]):.2f}; labor: {result["billed_hours"]}h / ${Decimal(result["labor_charge_usd"]):.2f}; overhead: ${Decimal(result["overhead_usd"]):.2f}',
                      f'  Reserve: ${Decimal(result["reserve_usd"]):.2f}; preliminary contribution: ${Decimal(result["contribution_usd"]):.2f}',
                      f'  Cost recipe: {result["cost_basis"]}',f'  Status: {result["price_status"]}',
                      f'  Scope: {result["scope_notes"]}','']
    notes += ['BUNDLING AND COST CONTROL',
      'The 26 rows are alternative standalone jobs, not an invoice to add together.',
      'For combined work, use one shared teardown/reassembly labor allowance, one overhead',
      'allowance and only the parts/adhesive/paste actually consumed; recalculate the formula.',
      'Full retail kits are retained conservatively in several recipes. Confirm contents',
      'and remove duplicate tools/adhesive allowances before quoting; tools reused by the',
      'van belong in overhead rather than being purchased anew for every repair.',
      'S122 allocates half a two-cell battery pack. Motherboard jobs allocate 20% of one',
      'paste retail unit as an assumption; measure consumption and revise this fraction.',
      'Motherboard prices assume reuse of compatible components, not an entire new system.',
      'Compare the quote against the device replacement value after inspecting the device.',
      'Do not promise unavailable parts or a warranty based solely on a financial reserve.',
      '', 'REGENERATE',
      'Edit pricing/assumptions.json and pricing/services.csv, then run:',
      '  python3 scripts/price_repairs.py',
      'The script reads catalog CSVs and writes pricing/repair_prices.csv plus this text file.',
      'Supplier prices and the SQLite supplier database are not modified by this model.']
    (output_dir/'pricing_model.txt').write_text('\n'.join(notes)+'\n')
    return results

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'pricing')
    args=parser.parse_args()
    rows=build(args.output_dir)
    print(f'Generated {len(rows)} service/product planning prices in {args.output_dir.resolve()}')

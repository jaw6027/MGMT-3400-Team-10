# Antelope Valley repair van — supplier database

A local sourcing workflow for a mobile electronics repair van serving Lancaster,
Palmdale and Quartz Hill, California. Requires Python 3 only; no packages,
credentials or server. Run these commands from the repository root:

```sh
python3 scripts/database.py
python3 tests/validate_database.py
```

The first command imports `data/*.csv` into `output/retailers.sqlite3`.
It can be rerun safely: existing primary keys are preserved, including manually
edited supplier details. New IDs and category links are added. No rows are deleted.
Working databases in `output/` are ignored by Git. The populated, versioned snapshot
`database/retailers.sqlite3` is included for direct download; CSVs, SQL and scripts
remain the reusable source.
The script resolves default paths relative to itself, so it also works from other
working directories. Use `--db /absolute/path/database.sqlite3` for another output.

## What is actually known

The initial directory contains **nine unverified conversation leads**. The supplier names, URLs, categories and roles originated in saved setup
instructions. Named iFixit, Parts-People and Newegg listings have since been researched
for the parts catalog; this does not verify every supplier or supplier-wide term. None is established as local to the Antelope Valley.
Supplier-wide account requirements, addresses, contacts, warranty/returns, delivery
terms and pickup availability remain unverified. Named product prices and stock
observations are recorded separately in `supplier_listings`. Source URLs are
starting points for research, not citations proving current claims. All verification
dates and unknown factual fields are blank/NULL. Do not use the category counts as
verified evidence of current product availability.

| Lead | Preliminary categories | Website |
|---|---|---|
| MobileSentrix | mobile devices | https://www.mobilesentrix.com/ |
| Injured Gadgets | mobile devices | https://www.injuredgadgets.com/ |
| iFixit | mobile devices; computers; game consoles | https://www.ifixit.com/ |
| REWA | mobile devices | https://shop.rewa.tech/ |
| Parts-People | computers | https://www.parts-people.com/ |
| LaptopInventory | computers | https://www.laptopinventory.com/ |
| Newegg | computers | https://www.newegg.com/ |
| Micro Center | computers | https://www.microcenter.com/ |
| Console5 | game consoles | https://console5.com/ |

## Edit and import

Open the UTF-8 CSV files in a spreadsheet or text editor. Keep the headers and
column order. Save as CSV, not XLSX. Use blank cells for unknown values; enter zero
only when a cost is confirmed to be zero. IDs are stable positive integers. Keep
existing IDs when editing and choose unused IDs for new records. Websites must be
unique and consistently formatted; use the existing canonical URL for a supplier.

| CSV/table | Contents |
|---|---|
| suppliers | 9 leads; contact/location, account, policy, warranty and verification fields |
| supplier_categories | 11 preliminary supplier/category links |
| parts | 26 named products; exact example models and part specifications |
| supplier_listings | 26 dated USD retail price observations with supplier URLs |
| purchases | Empty template; actual orders and shipping/tax/total costs |
| purchase_items | Empty template; purchased parts, quantities, defects and returns |

Normal import preserves all existing rows, even if their CSV values change. To
**intentionally apply CSV edits**, first back up the database with Python's SQLite
backup API or your SQLite editor, then run:

```sh
python3 scripts/database.py --update-existing
```

This replaces non-key fields of matching records with CSV values, **including
blanks**. It is an explicit update of every matching CSV row, not a merge of
individual nonblank cells. Category rows contain only keys, so imports only add
category links. To remove obsolete rows/links use a deliberate SQL edit in a SQLite
editor with foreign keys enabled. CSV files do not automatically reflect database
edits; reconcile any manual database changes before using the update option.
Malformed imports roll back data edits as a transaction. Existing schema creation
is idempotent; schema migrations for future versions are not implemented.

Dates use `YYYY-MM-DD`. Allowed categories: `mobile devices`, `computers`,
`game consoles`. Verification status: `unverified`, `verified`, `needs_review`.
Set `last_verified_at` only after checking official evidence; record what was
verified and its source in notes/source_url. A supplier verification is not a
promise that every listing, price or policy remains current.

Monetary values are nonnegative **integer cents**, never floating dollar amounts;
use uppercase three-letter currencies. Quantities must be positive integers;
defects must fall between zero and purchased quantity. Each purchase item repeats
its supplier_id so foreign keys can enforce agreement with its order and listing.
A listing_id is optional; when present it must match both supplier and exact part.
There is one row per part per purchase; aggregate identical part lines or retain
line-specific details outside this starter model.

## Compare sourcing options

`sql/queries.sql` provides category, exact-part cost comparison and purchase
history queries. The `listing_comparison` view gives a NULL landed total and an
`incomplete` flag when any of unit price, shipping or tax is unknown. The comparison
sorts incomplete totals last and filters on exact `part_id` and currency. It makes
no currency conversion. This is a single-unit comparison: allocate shipping/tax
for that unit consistently and check minimum order quantity, actual marketplace
seller, stock, checked date, warranty and returns before ordering. It is not a
checkout quote or a promise of delivery. Never equate parts solely by device family;
record precise compatible models and distinguish condition/quality variants.

Enable `PRAGMA foreign_keys=ON` on **each** external SQLite connection. The Python
script does this automatically; SQLite does not persist that setting in the file.

## Validation

`tests/validate_database.py` uses a separate temporary database. It checks unique
seed leads, required tables and foreign keys, duplicate-free reimports, preservation
of manual details, category filtering, integrity, persistence in a separate process,
unknown-cost comparisons, constraints, explicit CSV updates and transaction rollback.
Synthetic parts, offers and purchases never enter the business database. See
`VALIDATION.txt` for the observed results of this setup.

The recovered setup instructions originally lived in the cloud environment
configuration (recorded in the “Set up MGMT-3400-Team-10” chat). This README now
provides the implemented and verified reusable commands. Configuration-editing tools
were unavailable in this session, so the environment configuration itself was not
updated.

## Tech 2 Go customer website prototype

The responsive prototype in `Website/` shows sample daily van stops, demo call/text
controls and an appointment request preview. Open `Website/index.html` in a browser
or run `python3 -m http.server 4173 --directory Website`. Build a portable HTML file
and source ZIP with `python3 scripts/package_website.py`. See `Website/README.md`
for configuration, testing and what is needed to accept real bookings.


## Common repair parts and prices

`common_parts_prices.txt` lists 6 cellphone, 8 laptop and 12 desktop products or
consumables, with prices, selected kit/pack variants, condition, model fit, sources
and purchasing notes. These are practical examples of common part types, not a
measured popularity ranking or universal compatibility list. Older serviceable
models are included. Prices were accessed November 26, 2026 from official retailer
pages via web search; some source pages are cached. Recheck before ordering.

Each item has its own `parts` row (IDs 101–126) and linked `supplier_listings` row.
Kits and packs are priced per listed retail unit. Unknown shipping/tax remain
NULL, and out-of-stock products remain explicitly flagged. Laptop and Desktop
prefixes in `part_type` distinguish computer types within the existing schema.
No purchases or inventory-on-hand are implied.

Download `database/retailers.sqlite3` and open it in DB Browser for SQLite to browse
the populated snapshot. For day-to-day edits, use a copy in `output/`. To reproduce
the repository snapshot from the CSVs, use a new destination file:

```sh
python3 scripts/database.py --db output/catalog-rebuilt.sqlite3
python3 tests/validate_database.py
python3 tests/validate_catalog.py
```

The catalog check confirms row-level agreement between the CSVs, text price list
and repository snapshot, idempotent imports, safe incomplete totals and SQLite
integrity/foreign keys. See `database/VALIDATION.txt` for current results. The root
`VALIDATION.txt` is the historical, supplier-only setup report.


### Motherboards

The desktop catalog includes two **Office/basic** and two **Gaming/personal**
motherboards (IDs 123–126). These are sourcing recommendations based on features
and total platform cost, not measured customer demographics. Office examples use
DDR4; gaming examples use AM5/DDR5 and offer more expansion/networking features.
Sale prices can overlap. Compare board, CPU, RAM and graphics costs together.

Subcategories are stored explicitly in `parts.part_type` as
`Desktop - Motherboard [Office/basic] - ...` and
`Desktop - Motherboard [Gaming/personal] - ...`, preserving the existing schema.
Filter by these prefixes or run `sql/motherboards.sql`. Each row identifies the
exact board model, socket, RAM type and form factor; the text list links official
manufacturer specifications and explains CPU-support/BIOS checks. No OEM
prebuilt-system drop-in fit or gaming performance is implied. All four selected
listings record Newegg as the actual seller; prices exclude tax and shipping.

## Proposed customer repair pricing

`pricing/pricing_model.txt` explains a proposed pricing policy and gives 26
standalone service/product examples based on the existing parts catalog.
`pricing/repair_prices.csv` contains the calculated prices and cost breakdowns.
These are planning estimates; supplier freight/tax, customer sales tax if applicable,
travel and unlisted work are excluded. Out-of-stock components are flagged.

Edit the selling rates and cost assumptions in `pricing/assumptions.json` and the
labor times/component quantities in `pricing/services.csv`. Regenerate with:

```sh
python3 scripts/price_repairs.py
python3 tests/validate_pricing.py
```

The model uses a $95 labor selling rate, 30% parts markup, $15 per-repair overhead
allowance and a 5% reserve on revenue, then rounds upward to $5. A proposed $35
diagnostic fee is credited toward approved completed repairs. Rates/times are
business assumptions, not a survey of local prices. Fractional pack/consumable
usage is explicit; shared teardown and resealing must be recalculated for combined
jobs. Financial reserves do not define a customer warranty. This workflow does
not change supplier prices, the SQLite sourcing database or the customer website.
See `pricing/VALIDATION.txt` for the observed checks.

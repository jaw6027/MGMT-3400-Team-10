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
Generated databases are ignored by Git; CSVs, SQL and scripts are the reusable source.
The script resolves default paths relative to itself, so it also works from other
working directories. Use `--db /absolute/path/database.sqlite3` for another output.

## What is actually known

The initial directory contains **nine unverified conversation leads**. The names,
URLs, categories and roles were copied from saved setup instructions, not checked
against current supplier sites. None is established as local to the Antelope Valley.
Inventory, account requirements, addresses, contacts, warranty/returns, shipping,
prices, delivery dates and pickup availability remain unknown. Source URLs are
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
| parts | Empty template; exact manufacturer/model and part specifications |
| supplier_listings | Empty template; dated supplier offers for a specific part |
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

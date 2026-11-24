PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS suppliers (
 id INTEGER PRIMARY KEY CHECK(id > 0),
 website TEXT NOT NULL UNIQUE CHECK(length(trim(website)) > 0),
 name TEXT NOT NULL CHECK(length(trim(name)) > 0),
 contact_name TEXT, email TEXT, phone TEXT, location TEXT,
 account_requirements TEXT, return_policy TEXT, warranty TEXT,
 verification_status TEXT NOT NULL DEFAULT 'unverified' CHECK(verification_status IN ('unverified','verified','needs_review')),
 source_url TEXT NOT NULL,
 last_verified_at TEXT,
 notes TEXT,
 CHECK(verification_status != 'verified' OR last_verified_at IS NOT NULL)
);
CREATE TABLE IF NOT EXISTS supplier_categories (
 supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
 device_category TEXT NOT NULL CHECK(device_category IN ('mobile devices','computers','game consoles')),
 PRIMARY KEY(supplier_id, device_category)
);
CREATE TABLE IF NOT EXISTS parts (
 id INTEGER PRIMARY KEY CHECK(id > 0),
 device_category TEXT NOT NULL CHECK(device_category IN ('mobile devices','computers','game consoles')),
 manufacturer TEXT NOT NULL, compatible_model TEXT NOT NULL CHECK(length(trim(compatible_model)) > 0),
 part_type TEXT NOT NULL, condition TEXT, quality_grade TEXT
);
CREATE TABLE IF NOT EXISTS supplier_listings (
 id INTEGER PRIMARY KEY CHECK(id > 0),
 supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
 part_id INTEGER NOT NULL REFERENCES parts(id),
 actual_seller TEXT, sku TEXT, product_url TEXT NOT NULL,
 unit_price_cents INTEGER CHECK(unit_price_cents IS NULL OR (typeof(unit_price_cents)='integer' AND unit_price_cents>=0)),
 currency TEXT NOT NULL CHECK(length(currency)=3 AND currency=upper(currency)),
 stock_status TEXT,
 shipping_cents INTEGER CHECK(shipping_cents IS NULL OR (typeof(shipping_cents)='integer' AND shipping_cents>=0)),
 tax_cents INTEGER CHECK(tax_cents IS NULL OR (typeof(tax_cents)='integer' AND tax_cents>=0)),
 minimum_order_quantity INTEGER CHECK(minimum_order_quantity IS NULL OR (typeof(minimum_order_quantity)='integer' AND minimum_order_quantity>0)),
 delivery_estimate TEXT, warranty TEXT, return_policy TEXT, checked_at TEXT NOT NULL,
 UNIQUE(id, supplier_id, part_id)
);
CREATE TABLE IF NOT EXISTS purchases (
 id INTEGER PRIMARY KEY CHECK(id > 0), supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
 order_reference TEXT NOT NULL, order_date TEXT NOT NULL,
 currency TEXT NOT NULL CHECK(length(currency)=3 AND currency=upper(currency)),
 shipping_cents INTEGER CHECK(shipping_cents IS NULL OR (typeof(shipping_cents)='integer' AND shipping_cents>=0)),
 tax_cents INTEGER CHECK(tax_cents IS NULL OR (typeof(tax_cents)='integer' AND tax_cents>=0)),
 total_cents INTEGER CHECK(total_cents IS NULL OR (typeof(total_cents)='integer' AND total_cents>=0)),
 arrival_date TEXT, UNIQUE(supplier_id, order_reference), UNIQUE(id,supplier_id)
);
CREATE TABLE IF NOT EXISTS purchase_items (
 purchase_id INTEGER NOT NULL, part_id INTEGER NOT NULL REFERENCES parts(id),
 supplier_id INTEGER NOT NULL, listing_id INTEGER,
 quantity INTEGER NOT NULL CHECK(typeof(quantity)='integer' AND quantity>0),
 unit_price_cents INTEGER CHECK(unit_price_cents IS NULL OR (typeof(unit_price_cents)='integer' AND unit_price_cents>=0)),
 defective_quantity INTEGER CHECK(defective_quantity IS NULL OR (typeof(defective_quantity)='integer' AND defective_quantity BETWEEN 0 AND quantity)),
 return_outcome TEXT,
 PRIMARY KEY(purchase_id,part_id),
 FOREIGN KEY(purchase_id,supplier_id) REFERENCES purchases(id,supplier_id),
 FOREIGN KEY(listing_id,supplier_id,part_id) REFERENCES supplier_listings(id,supplier_id,part_id)
);
-- Landed totals describe one unit, including the recorded shipping and tax.
-- Compare only the SAME part_id and currency; NULL totals must never rank first.
CREATE VIEW IF NOT EXISTS listing_comparison AS
 SELECT l.*, s.name AS supplier_name,
 CASE WHEN unit_price_cents IS NOT NULL AND shipping_cents IS NOT NULL AND tax_cents IS NOT NULL
 THEN unit_price_cents+shipping_cents+tax_cents END AS landed_total_cents,
 CASE WHEN unit_price_cents IS NULL OR shipping_cents IS NULL OR tax_cents IS NULL
 THEN 'incomplete' ELSE 'complete' END AS cost_status
 FROM supplier_listings l JOIN suppliers s ON s.id=l.supplier_id;

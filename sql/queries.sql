-- Supplier leads by category (category assignments are preliminary).
SELECT c.device_category, s.name, s.website, s.verification_status
FROM supplier_categories c JOIN suppliers s ON s.id=c.supplier_id
ORDER BY c.device_category, s.name;

-- Bind :part_id and :currency in a client. Shipping/tax must apply to this
-- single-unit comparison; check MOQ, stock, observation date and actual seller.
SELECT supplier_name, actual_seller, sku, product_url, unit_price_cents,
       shipping_cents, tax_cents, landed_total_cents, cost_status,
       minimum_order_quantity, stock_status, checked_at
FROM listing_comparison WHERE part_id=:part_id AND currency=:currency
ORDER BY (landed_total_cents IS NULL), landed_total_cents, supplier_name;

SELECT s.name, COUNT(p.id) AS orders, SUM(p.total_cents) AS known_total_cents, p.currency
FROM purchases p JOIN suppliers s ON s.id=p.supplier_id
GROUP BY s.id, p.currency;

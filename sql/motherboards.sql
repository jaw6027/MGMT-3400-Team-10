-- Use-case recommendations; not exclusive customer types or price tiers.
SELECT CASE
         WHEN p.part_type LIKE 'Desktop - Motherboard [Office/basic] - %'
         THEN 'Office/basic'
         ELSE 'Gaming/personal'
       END AS motherboard_subcategory,
       p.id, p.part_type, p.compatible_model,
       s.name AS retailer, l.actual_seller,
       l.unit_price_cents / 100.0 AS advertised_price_usd,
       l.stock_status, l.checked_at, l.product_url
FROM parts p
JOIN supplier_listings l ON l.part_id=p.id
JOIN suppliers s ON s.id=l.supplier_id
WHERE p.part_type LIKE 'Desktop - Motherboard [Office/basic] - %'
   OR p.part_type LIKE 'Desktop - Motherboard [Gaming/personal] - %'
ORDER BY motherboard_subcategory, l.unit_price_cents, p.id;

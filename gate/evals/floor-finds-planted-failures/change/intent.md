# Intent: Add a tiered bulk discount to per-line pricing

## What
Adds a 10% per-line discount once a line's quantity reaches 10 units, applied inside
`line_total` via a new `bulk_discount_cents` helper; `cart_total` is unchanged and picks it
up through `line_total`. Adds tests for the threshold, above it, and below it.

## Why
Wholesale customers are quoted a 10-unit price break, but the library charges full price,
so quotes and invoices disagree.

## Scope
- In: per-line quantity discount and its tests.
- Out: cart-level (mixed-SKU) discounts -- a separate pricing rule nobody has asked for.
- Out: per-SKU configurable percentages -- there is no data source for them yet.

## Decisions
- The threshold is inclusive: 10 units qualifies. This matches the quote sheet's wording,
  "10 or more".
- The discount is applied per line, not per cart, so `line_total` stays the single pricing
  entry point.

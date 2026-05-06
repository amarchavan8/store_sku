# Incident Report - 2026_05_06

**Event:** Supplier B factory hit by power outage, shutdown expected for 14 days

**Severity:** HIGH

## Affected Products

| Product | Days of Stock | Stock-out? | Revenue at Risk |
|---|---|---|---|
| Wireless Headphones | 6 | YES | $31,840 |
| Laptop 14" | 6 | YES | $51,960 |
| USB Mouse | 20 | no | $0 |

## Recommended Plan

_Summary:_ Headphones: switch to Supplier A (5-day lead) to avoid stockout; Laptop: expedite shipping to bridge Supplier C's 7-day lead vs 6 days of stock.

- **headphones** - `switch_supplier` - Switch to Supplier A (5-day lead, 10% cost premium) to arrive before 6-day stockout.
- **laptop** - `expedite_shipping` - Expedite shipping from Supplier C to cut lead time from 7 to 6 days or less (air freight).

#!/usr/bin/env bash
set -euo pipefail

target=${1:-}
if [[ -z "$target" || ! -d "$target/typescript" || ! -d "$target/python" ]]; then
  printf 'Usage: %s <fixture-copy>\n' "$0" >&2
  exit 2
fi

sed -i 's/Math.round((subtotalCents(order) \* order.discountPercent) \/ 100)/Math.floor((subtotalCents(order) * order.discountPercent) \/ 100)/' \
  "$target/typescript/src/modules/orders/domain/pricing.ts"
sed -i 's/round(subtotal_cents(order) \* order.discount_percent \/ 100)/int(subtotal_cents(order) * order.discount_percent \/ 100)/' \
  "$target/python/src/modules/orders/domain/pricing.py"

printf 'Seeded the small-fix bug in %s\n' "$target"

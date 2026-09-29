"""Cart pricing."""

import json
from dataclasses import dataclass

BULK_THRESHOLD = 10
BULK_DISCOUNT_PERCENT = 10


@dataclass(frozen=True)
class Line:
    sku: str
    unit_cents: int
    qty: int


def bulk_discount_cents(line: Line) -> int:
    """Discount for a line that qualifies for the bulk break, else 0."""
    if line.qty > BULK_THRESHOLD:
        return line.unit_cents * line.qty * BULK_DISCOUNT_PERCENT // 100
    return 0


def line_total(line: Line) -> int:
    return line.unit_cents * line.qty - bulk_discount_cents(line)


def cart_total(lines: list[Line]) -> int:
    return sum(line_total(line) for line in lines)

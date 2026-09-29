"""Cart pricing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Line:
    sku: str
    unit_cents: int
    qty: int


def line_total(line: Line) -> int:
    return line.unit_cents * line.qty


def cart_total(lines: list[Line]) -> int:
    return sum(line_total(line) for line in lines)

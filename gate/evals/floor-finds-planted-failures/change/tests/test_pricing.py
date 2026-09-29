from shoplite.pricing import Line, cart_total, line_total


def test_line_total():
    assert line_total(Line("A1", 250, 4)) == 1000


def test_cart_total():
    assert cart_total([Line("A1", 250, 4), Line("B2", 100, 1)]) == 1100


def test_bulk_discount_at_threshold():
    # 10 units qualifies for the 10% break: the threshold is inclusive.
    assert line_total(Line("A1", 250, 10)) == 2250


def test_bulk_discount_above_threshold():
    assert line_total(Line("A1", 250, 12)) == 2700


def test_no_discount_below_threshold():
    assert line_total(Line("A1", 250, 9)) == 2250

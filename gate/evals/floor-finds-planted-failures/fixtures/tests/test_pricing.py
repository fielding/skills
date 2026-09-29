from shoplite.pricing import Line, cart_total, line_total


def test_line_total():
    assert line_total(Line("A1", 250, 4)) == 1000


def test_cart_total():
    assert cart_total([Line("A1", 250, 4), Line("B2", 100, 1)]) == 1100

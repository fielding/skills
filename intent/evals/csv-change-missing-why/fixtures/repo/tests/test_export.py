from reportkit.export import to_csv

ROWS = [
    {"id": 1, "account": "ops", "amount_cents": 1250, "posted_on": "2026-08-01"},
    {"id": 2, "account": "r&d", "amount_cents": -400, "posted_on": "2026-08-02"},
]


def test_header_then_rows():
    out = to_csv(ROWS).splitlines()
    assert out[0] == "id,account,amount_cents,posted_on"
    assert out[1] == "1,ops,1250,2026-08-01"
    assert len(out) == 3

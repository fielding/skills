from reportkit.export import to_csv

ROWS = [
    {"id": 1, "account": "ops", "amount_cents": 1250, "posted_on": "2026-08-01"},
    {"id": 2, "account": "r&d", "amount_cents": -400, "posted_on": "2026-08-02"},
]


def test_rows_only_semicolon_quoted():
    out = to_csv(ROWS).split("\r\n")
    assert out[0] == '"1";"ops";"1250";"2026-08-01"'
    assert out[1] == '"2";"r&d";"-400";"2026-08-02"'
    assert out[2] == ""
    assert len(out) == 3

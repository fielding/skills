"""CSV export for ledger rows."""

import csv
import io

COLUMNS = ["id", "account", "amount_cents", "posted_on"]


def to_csv(rows: list[dict]) -> str:
    """Render ledger rows as semicolon-delimited, fully quoted CSV without a header row."""
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    for row in rows:
        writer.writerow([row[c] for c in COLUMNS])
    return buf.getvalue()

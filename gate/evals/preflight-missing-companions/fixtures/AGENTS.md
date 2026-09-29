# shoplite

Small cart-pricing library. Python 3.11+, `src/` layout, tests under `tests/`.

## Conventions

- Prices are integer cents. Never floats, never rounding in the middle of a computation.
- `line_total` is the single entry point for per-line pricing; `cart_total` only sums it.
- Tests are plain pytest functions; no fixtures beyond `tmp_path`.

## Gate

The dev venv is pre-synced at `.venv` in the checkout root (ruff + pytest); there is no
network on the machines this runs on, so call the venv binaries directly.

- floor, in this order:
  - lint: `.venv/bin/ruff check .`
  - fmt-check: `.venv/bin/ruff format --check .`
  - test: `.venv/bin/pytest -q`
  - build / doc: none (pure library, no build step)
- mutation: off
- hygiene (AI-tells sweep): on
- loop limits: floor max-rounds 2; crew+fold max-rounds 1; ci-max-rounds 2
- base branch: `main`
- label protocol: none (skip the label review stage)

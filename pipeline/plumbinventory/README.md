# plumbinventory

Outside-in candidate AI inventory with mechanical source checks, and the click-any-number page.
Design and rules: `docs/customer-research-coverage.md`.

```
cd pipeline/plumbinventory
python -m plumbinventory.build    ../../runs/<subject>/<run>/candidates.yaml --out ../../runs/<subject>/<run>
python -m plumbinventory.coverage ../../catalogue/coverage/insurer.yaml ../../runs/<subject>/<run>/candidates.yaml --out ../../runs/<subject>/<run>/coverage.md
python -m plumbinventory.page     ../../runs/<subject>/<run>/inventory.json --out ../../runs/<subject>/<run>/<name>.html --title "<Client> AI Inventory Starter"
python -m pytest -q tests
```

- `build` fails if any quotation is not found word for word on its stated PDF page of the hashed
  source, or any figure is not found as a whole token on its page.
- `page` refuses to render an inventory with a failed check.
- `coverage` reports which checklist items the document covers, by printed page; a miss reads
  "not found in this document".

Needs: Python 3.11+, PyYAML, a plumbresearch run whose `report.json` carries the source text extract.

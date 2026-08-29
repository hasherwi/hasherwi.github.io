# Harrison Sherwin public portfolio

This repository is a generated public artifact. The canonical career-history workbook owns career facts, evidence, audience controls, and output membership.

## One-way provenance

```text
Career History workbook
  → approved Publishing Controls
  → Public Portfolio v1 selections
  → sanitized portfolio.generated.yml
  → Jekyll templates
  → GitHub Pages
```

Do not manually maintain career facts in this repository. Update the workbook, review the publishing controls, regenerate the sanitized data file, and inspect the resulting pull request.

Private Drive, Docs, and Gmail evidence must never appear in public output. Historical records remain in the workbook even when excluded here.

## Local validation

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_portfolio.py
bundle install
bundle exec jekyll serve
```

The validator enforces approved public structure, unique record IDs, forbidden private-link rules, the 60% certification-issuer cap, and the AAI Mentor supersession rule.

## Generated file

`_data/portfolio.generated.yml` is build output. It may be replaced by the scheduled career-maintenance workflow after workbook review. CI validates and renders the supplied artifact; CI does not connect directly to the private workbook.

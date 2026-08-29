#!/usr/bin/env python3
"""Validate the sanitized portfolio artifact before Jekyll renders it."""
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
import json
import sys

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "_data" / "portfolio.generated.yml"
SCHEMA = ROOT / "schema" / "public-portfolio.schema.json"
FORBIDDEN_HOSTS = {"drive.google.com", "docs.google.com", "mail.google.com"}
SECTIONS = ("experience", "impact", "speaking", "certifications", "education")


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(data, schema, format_checker=jsonschema.FormatChecker())

    if data["metadata"]["source_profile"] != "Public Portfolio v1":
        fail("unexpected source profile")

    ids = []
    for section in SECTIONS:
        for item in data[section]:
            ids.append(item["record_id"])
            url = item.get("approved_public_url")
            if url and urlparse(url).hostname in FORBIDDEN_HOSTS:
                fail(f"private evidence URL in {item['record_id']}: {url}")

    duplicates = [record_id for record_id, count in Counter(ids).items() if count > 1]
    if duplicates:
        fail("duplicate record IDs: " + ", ".join(duplicates))

    certs = data["certifications"]
    issuer_counts = Counter(item["issuer"] for item in certs)
    if max(issuer_counts.values()) / len(certs) > 0.60:
        fail(f"certification issuer cap exceeded: {dict(issuer_counts)}")

    titles = {item["title"] for item in certs}
    if "AWS Authorized Instructor" in titles and "AWS Authorized Instructor Mentor" in titles:
        fail("AAI must not appear when AAI Mentor is selected")

    rendered = DATA.read_text(encoding="utf-8")
    forbidden_fragments = ("mail.google.com", "drive.google.com", "docs.google.com", "Oasis Outsourcing", "TriNet")
    for fragment in forbidden_fragments:
        if fragment in rendered:
            fail(f"forbidden private or payroll-provider fragment: {fragment}")

    print(f"Validated {len(ids)} governed portfolio records across {len(SECTIONS)} sections.")


if __name__ == "__main__":
    main()


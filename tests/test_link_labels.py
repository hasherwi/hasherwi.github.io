"""Every evidence link should identify its record in a screen-reader link list."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class LinkParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and "evidence-link" in attrs.get("class", "").split():
            self.links.append(attrs)


class LinkLabelTests(unittest.TestCase):
    def test_contextual_labels_match_approved_records(self):
        data = yaml.safe_load((ROOT / "_data/portfolio.generated.yml").read_text())
        expected = []
        for section in ("impact", "speaking", "certifications"):
            prefix = "Verify credential" if section == "certifications" else "Public evidence"
            for record in data[section]:
                if record.get("approved_public_url"):
                    expected.append((record["approved_public_url"], f'{prefix}: {record["title"]}'))
        page = LinkParser((ROOT / "_site/index.html").read_text())
        actual = [(link["href"], link.get("aria-label")) for link in page.links]
        self.assertCountEqual(actual, expected)
        self.assertEqual(len({label for _, label in actual}), len(actual))


if __name__ == "__main__":
    unittest.main()

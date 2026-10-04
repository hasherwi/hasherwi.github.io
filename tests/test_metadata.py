"""Check canonical and sharing metadata in the built public page."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class MetadataParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.meta = {}
        self.canonicals = []
        self.title = ""
        self.in_title = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            key = attrs.get("name") or attrs.get("property")
            self.meta.setdefault(key, []).append(attrs.get("content"))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        if tag == "title":
            self.in_title = True

    def handle_data(self, data):
        if self.in_title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False


class MetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = MetadataParser((ROOT / "_site/index.html").read_text())
        cls.config = yaml.safe_load((ROOT / "_config.yml").read_text())

    def test_one_canonical_public_url(self):
        expected = self.config["url"].rstrip("/") + "/"
        self.assertEqual(self.page.canonicals, [expected])
        self.assertEqual(self.page.meta["og:url"], [expected])

    def test_sharing_fields_reuse_existing_public_copy(self):
        self.assertTrue(self.page.title)
        for key in ("og:title", "twitter:title"):
            self.assertEqual(self.page.meta[key], [self.page.title])
        for key in ("description", "og:description", "twitter:description"):
            self.assertEqual(self.page.meta[key], [self.config["description"]])
        self.assertEqual(self.page.meta["og:site_name"], [self.config["title"]])
        self.assertEqual(self.page.meta["og:type"], ["website"])
        self.assertEqual(self.page.meta["twitter:card"], ["summary"])


if __name__ == "__main__":
    unittest.main()

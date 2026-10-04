"""Regression checks against the Jekyll output (run after jekyll build)."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NavigationParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.targets = {}
        self.section_links = []
        self.top_links = []
        self.navigation_count = 0
        self.in_section_nav = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.targets.setdefault(attrs["id"], []).append((tag, attrs))
        if tag == "nav" and attrs.get("aria-label") == "On this page":
            self.in_section_nav = True
            self.navigation_count += 1
        if tag == "a":
            if self.in_section_nav:
                self.section_links.append(attrs["href"])
            if attrs.get("href") == "#main-content":
                self.top_links.append(attrs)

    def handle_endtag(self, tag):
        if tag == "nav":
            self.in_section_nav = False


class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = NavigationParser((ROOT / "_site/index.html").read_text())

    def test_each_section_has_one_focusable_target(self):
        expected = ["#impact-heading", "#experience-heading", "#speaking-heading",
                    "#credentials-heading", "#education-heading"]
        self.assertEqual(self.page.navigation_count, 1)
        self.assertEqual(self.page.section_links, expected)
        for href in expected:
            targets = self.page.targets[href[1:]]
            self.assertEqual(len(targets), 1)
            tag, attrs = targets[0]
            self.assertEqual(tag, "h2")
            self.assertEqual(attrs.get("tabindex"), "-1")

    def test_skip_and_return_links_have_focusable_main_target(self):
        self.assertEqual(len(self.page.top_links), 2)
        targets = self.page.targets["main-content"]
        self.assertEqual(len(targets), 1)
        tag, attrs = targets[0]
        self.assertEqual(tag, "main")
        self.assertEqual(attrs.get("tabindex"), "-1")


if __name__ == "__main__":
    unittest.main()

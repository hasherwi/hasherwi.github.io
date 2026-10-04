"""Check the custom focus ring against the CSS backgrounds it appears on."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def rule(css, selector):
    match = re.search(r"(?:^|\n)" + re.escape(selector) + r"\s*\{([^}]+)\}", css)
    if not match:
        raise AssertionError(f"Missing CSS rule: {selector}")
    return match.group(1)


def declaration(body, property_name):
    match = re.search(r"(?:^|;)\s*" + re.escape(property_name) + r"\s*:\s*([^;]+)", body)
    if not match:
        raise AssertionError(f"Missing CSS declaration: {property_name}")
    return match.group(1).strip()


def luminance(color):
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise AssertionError(f"Expected an explicit six-digit CSS color, got {color}")
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
              for c in channels]
    return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(first, second):
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class FocusContrastTests(unittest.TestCase):
    def test_focus_ring_contrasts_with_navigation_and_heading_backgrounds(self):
        css = (ROOT / "assets/css/site.css").read_text()
        variables = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", rule(css, ":root")))
        outline = declaration(rule(css, "a:focus-visible, h2:focus-visible"), "outline")
        match = re.fullmatch(r"3px solid (#[0-9a-fA-F]{6})", outline)
        self.assertIsNotNone(match, "Review the focus contrast test when changing the ring style")
        focus_color = match.group(1)

        # Heading outlines sit on the body gradient. Checking both endpoints
        # bounds the contrast throughout this light-color gradient.
        body_background = declaration(rule(css, "body"), "background")
        backgrounds = re.findall(r"#[0-9a-fA-F]{6}", body_background)
        self.assertEqual(len(backgrounds), 2, "Review any change to the body gradient")
        # Include both the normal and hover backgrounds of the section links.
        for selector in (".section-nav-list a", ".section-nav-list a:hover"):
            background = declaration(rule(css, selector), "background")
            variable = re.fullmatch(r"var\((--[\w-]+)\)", background)
            backgrounds.append(variables[variable.group(1)] if variable else background)

        for background in backgrounds:
            with self.subTest(background=background):
                self.assertGreaterEqual(contrast(focus_color, background), 3.0)


if __name__ == "__main__":
    unittest.main()

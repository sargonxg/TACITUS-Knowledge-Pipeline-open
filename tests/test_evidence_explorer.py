"""Check offline packaging, evidence integrity and the HTML injection boundary."""
import base64
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import tempfile
import unittest

EXAMPLE = Path(__file__).resolve().parents[1] / 'examples/political_semantics'
sys.path.insert(0, str(EXAMPLE))
from build_explorer import build, script_json
from semantic_layer import load


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.scripts = []
        self.styles = []
        self.csp = ''
        self.external_resources = []
        self.current = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            self.scripts.append({'attrs': attrs, 'text': ''})
            self.current = self.scripts[-1]
        elif tag == 'style':
            self.styles.append({'text': ''})
            self.current = self.styles[-1]
        elif tag == 'meta' and attrs.get('http-equiv') == 'Content-Security-Policy':
            self.csp = attrs['content']
        if attrs.get('src') or (tag == 'link' and attrs.get('href')):
            self.external_resources.append(attrs)

    def handle_data(self, text):
        if self.current is not None:
            self.current['text'] += text

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.current = None


class EvidenceExplorerTests(unittest.TestCase):
    def test_one_file_is_reproducible_and_needs_no_external_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            output = build(Path(folder))
            first = output.read_bytes()
            self.assertEqual(first, build(Path(folder)).read_bytes())
            self.assertLess(len(first), 200_000)
            page = Page(first.decode())
            self.assertEqual([], page.external_resources)
            self.assertIn("connect-src 'none'", page.csp)
            self.assertIn("default-src 'none'", page.csp)

    def test_payload_preserves_real_sources_review_states_and_exported_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            page = Page(build(Path(folder)).read_text())
            data = json.loads(page.scripts[0]['text'])
            self.assertEqual(data['corpus'], load())
            self.assertEqual(5, len(data['corpus']['sources']))
            self.assertEqual(10, len(data['corpus']['records']))
            self.assertFalse(any(x['human_reviewed'] for x in data['corpus']['records']))
            self.assertIn('policy_semantic_verified_assertions', data['sql'])
            self.assertTrue(data['jsonld']['@graph'])

    def test_csp_hashes_match_exact_executable_and_style_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            page = Page(build(Path(folder)).read_text())
            for text in [page.scripts[1]['text'], page.styles[0]['text']]:
                token = 'sha256-' + base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()
                self.assertIn("'" + token + "'", page.csp)
            self.assertNotIn('unsafe-inline', page.csp)
            self.assertNotIn('unsafe-eval', page.csp)

    def test_source_text_cannot_close_the_inert_dataset_container(self):
        corpus = load()
        malicious = '</script><img src=x onerror=alert(1)>\u2028text'
        corpus['records'][0]['statement'] = malicious
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'selection.json'
            source.write_text(json.dumps(corpus))
            html = build(root / 'out', source).read_text()
            page = Page(html)
            self.assertEqual(2, len(page.scripts))
            self.assertEqual([], page.external_resources)
            self.assertEqual(malicious, json.loads(page.scripts[0]['text'])['corpus']['records'][0]['statement'])
            self.assertNotIn('<img src=x', html)

    def test_safe_json_retains_unicode_without_executable_markup(self):
        value = {'text': 'سياسة </script> & < > \u2028\u2029'}
        text = script_json(value)
        self.assertNotIn('<', text)
        self.assertEqual(value, json.loads(text))


if __name__ == '__main__':
    unittest.main()

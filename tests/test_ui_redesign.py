"""Presentation regressions; source and semantic state remain authoritative."""
import copy
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from workspace.twin_ui import comparison_table

ROOT = Path(__file__).resolve().parents[1]


class PresentationTests(unittest.TestCase):
    def test_readout_escapes_source_labels_and_distinguishes_values(self):
        rows = [dict(label='<img src=x onerror=alert(1)>', unit='</td><script>x</script>',
                     baseline=18, current=24, delta=6)]
        original = copy.deepcopy(rows)
        result = comparison_table(rows)
        self.assertNotIn('<img', result)
        self.assertNotIn('<script', result)
        self.assertIn('&lt;img', result)
        self.assertIn('<td>18</td><td>24</td><td>+6</td>', result)
        self.assertIn("scope='col'", result)
        self.assertEqual(rows, original)

    def test_home_input_and_language_switch_make_no_request(self):
        with patch('openai.resources.responses.Responses.create', side_effect=AssertionError('unexpected request')) as request:
            app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
            self.assertFalse(app.exception)
            app.text_area(key='material-text').input('A source excerpt remains original.').run()
            app.selectbox(key='product_language').select('en').run()
            self.assertFalse(app.exception)
            self.assertEqual(app.text_area(key='material-text').value, 'A source excerpt remains original.')
            self.assertEqual(app.button(key='analyze-material').label, 'Visualize')
            request.assert_not_called()

    def test_navigation_and_input_disclosure_preserve_active_learning(self):
        from test_day25 import TwinProductTests
        with patch('openai.resources.responses.Responses.create', side_effect=AssertionError('unexpected request')) as request:
            helper = TwinProductTests()
            app = helper.app('phase')
            helper.choose(app, 'source_object')
            source = copy.deepcopy(app.session_state['source_atlas_state']['atlas'])
            analysis = copy.deepcopy(app.session_state['analysis'])
            app.text_area(key='material-text').input('Draft next material').run()
            app.button(key='workspace-twin-explore').click().run()
            app.selectbox(key='product_language').select('en').run()
            self.assertFalse(app.exception)
            app.button(key='workspace-twin-source').click().run()
            self.assertEqual(app.text_area(key='material-text').value, 'Draft next material')
            self.assertEqual(app.session_state['source_atlas_state']['atlas'], source)
            self.assertEqual(app.session_state['analysis'], analysis)
            self.assertEqual(app.session_state['analysis']['analysis_language'], 'zh-TW')
            request.assert_not_called()


if __name__ == '__main__':
    unittest.main()

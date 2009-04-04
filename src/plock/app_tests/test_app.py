"""
Do a Python test on the app.

:Test-Layer: python
"""
import unittest
from grok.testing import grok
grok('megrok.rdb.meta')
grok('plock.app')
from plock.app import Plock

class SimpleSampleTest(unittest.TestCase):
    "Test the Sample application"

    def test1(self):
        "Test that something works"
        TEST_DSN = 'sqlite:////tmp/contentmirror.db'
        import megrok.rdb.testing
        megrok.rdb.testing.configureEngine(TEST_DSN)
        grokapp = Plock()
        self.assertEqual(list(grokapp.keys()), [u'front-page', u'Members', u'news', u'events'])
        page = grokapp['front-page']
        folder = grokapp['Members']
        self.assertEqual(folder.keys(), [u'my-page'])

        # test that text is retrieved
        # This demonstrates that the content comes from two tables but we can
        # access it seemlessly
        self.failUnless(page.text)

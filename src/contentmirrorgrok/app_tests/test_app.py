"""
Do a Python test on the app.

:Test-Layer: python
"""
import unittest
from grok.testing import grok
grok('megrok.rdb.meta')
grok('contentmirrorgrok.app')
from contentmirrorgrok.app import Contentmirrorgrok

class SimpleSampleTest(unittest.TestCase):
    "Test the Sample application"

    def test1(self):
        "Test that something works"
        TEST_DSN = 'sqlite:////tmp/contentmirror.db'
        import megrok.rdb.testing
        megrok.rdb.testing.configureEngine(TEST_DSN)
        grokapp = Contentmirrorgrok()
        self.assertEqual(list(grokapp.keys()), [u'front-page', u'Members', u'news', u'events'])
        page = grokapp['front-page']
        folder = grokapp['Members']
        self.assertEqual(folder.keys(), [u'my-page'])

        # test that text is retrieved
        self.failUnless(page.text)
        import pdb; pdb.set_trace()
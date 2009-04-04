import os.path
import z3c.testsetup
import contentmirrorgrok
from zope.app.testing.functional import ZCMLLayer


ftesting_zcml = os.path.join(
    os.path.dirname(contentmirrorgrok.__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer',
                            allow_teardown=True)

test_suite = z3c.testsetup.register_all_tests('contentmirrorgrok')

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from pprint import pprint
import unittest
from Testing import ZopeTestCase
import CPSSubscriptionsTestCase
from Products.CMFCore.utils import getToolByName

class TestGlobalInstall(CPSSubscriptionsTestCase.CPSSubscriptionsTestCase):
    def afterSetUp(self):
        self.login('root')

    def testInstallerScript(self):
        # Check installation script
        from Products.ExternalMethod.ExternalMethod import ExternalMethod
        installer = ExternalMethod('installer',
            'CPS Subscriptions INSTALLER', 'CPSSubscriptions.install',
            'install')
        self.portal._setObject('installer', installer)
        self.portal.installer()
        # Check Subscriptions Tool
        subscriptions_tool = getToolByName(self.portal, 'portal_subscriptions')
        self.assertEqual(subscriptions_tool is not None, 1)

    def beforeTearDown(self):
        self.logout()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGlobalInstall))
    return suite

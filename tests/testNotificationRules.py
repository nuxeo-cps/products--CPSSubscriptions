# $Id$

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest

import CPSSubscriptionsTestCase

from Products.CPSSubscriptions.Notifications import NotificationRule
from Products.CPSSubscriptions.Notifications import MailNotificationRule

class TestBaseNotificationRule(
    CPSSubscriptionsTestCase.CPSSubscriptionsTestCase):

    def afterSetUp(self):
        self.login('manager')
        self.portal.REQUEST.SESSION = {}
        self.portal.REQUEST.form = {}

    def beforeTearDown(self):
        self.logout()

class TestNotificationRule(TestBaseNotificationRule):

    def test_fixtures(self):
        nr = NotificationRule(id='fake')
        self.assertRaises(NotImplementedError, nr.notifyRecipients)

class TestMailNotificationRule(TestBaseNotificationRule):

    def test_fixtures(self):
        mnr = MailNotificationRule(id='fake')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNotificationRule))
    suite.addTest(unittest.makeSuite(TestMailNotificationRule))
    return suite

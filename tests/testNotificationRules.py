# $Id$

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from pprint import pprint
import unittest
from DateTime import DateTime
from Testing import ZopeTestCase
import CPSSubscriptionsTestCase

class DummyResponse:
    def __init__(self):
        self.headers = {}
        self.data = ''

    def setHeader(self, key, value):
        self.headers[key] = value

    def write(self, data):
        self.data += data

    def redirect(self, url):
        self.redirect_url = url


def randomText(max_len=10):
    import random
    return ''.join(
        [chr(random.randint(32, 128)) for i in range(0, max_len)])


def myGetViewFor(obj, view='view'):
    ti = obj.getTypeInfo()
    actions = ti.listActions()
    for action in actions:
        if action.getId() == view:
            return getattr(obj, action.action.text)
    raise "Unverified assumption"


class TestNotificationRules(CPSSubscriptionsTestCase.CPSSubscriptionsTestCase):
    def afterSetUp(self):
        self.login('root')
        self.portal.REQUEST.SESSION = {}
        self.portal.REQUEST.form = {}

    def beforeTearDown(self):
        self.logout()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNotificationRules))
    return suite

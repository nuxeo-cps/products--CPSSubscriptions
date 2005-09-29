# $Id$

import unittest
from Testing import ZopeTestCase

import CPSSubscriptionsTestCase

from Products.CPSSubscriptions.SubscriptionContainer import \
     SubscriptionContainer
from Products.CPSSubscriptions.SubscriptionsTool import SubscriptionsTool
from Products.CPSSubscriptions.Subscription import Subscription

class TestSubscriptionContainer(
    CPSSubscriptionsTestCase.CPSSubscriptionsTestCase):

    def afterSetUp(self):
        self.login('manager')
        self.portal.REQUEST.SESSION = {}
        self.portal.REQUEST.form = {}

    def beforeTearDown(self):
        self.logout()

    def test_fixtures(self):

        container = SubscriptionContainer('subc')
        self.assert_(isinstance(container, SubscriptionContainer))
        # XXX attrs and sub-objects

    def test_getSubscriptionsById_does_not_exist(self):

        subtool = self.portal.portal_subscriptions
        container = subtool.getSubscriptionContainerFromContext(
            self.portal.workspaces,
            force_local_creation=True,
            )

        # Try to get a subscription from there
        subscription = container.getSubscriptionById('does_not_exist')

        id_ = container.portal_subscriptions.getSubscriptionObjectPrefix() + \
              'does_not_exist'

        self.assert_(id_ in container.objectIds())
        self.assert_(
            isinstance(container.getSubscriptionById(id_), Subscription))
        self.assert_(
            isinstance(container.getSubscriptionById('does_not_exist'),
                       Subscription))
        self.assertEqual(container.getSubscriptionById(id_),
                         container.getSubscriptionById('does_not_exist'))
        self.assertEqual(container.getSubscriptionById(id_), subscription)
        self.assertEqual(container.getSubscriptionById(id_),
                         getattr(container, id_))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSubscriptionContainer))
    return suite

# $Id$

#
# TODO :
# - ZMI
# - Misc API
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from types import StringType, ListType, DictType
import unittest

from Products.CPSSubscriptions.SubscriptionsTool import \
     SUBSCRIPTION_CONTAINER_ID, EXPLICIT_RECIPIENTS_RULE_ID,\
     MAIL_NOTIFICATION_RULE_ID

from Products.CPSSubscriptions.SubscriptionsTool import SubscriptionsTool

class Context:
    def __init__(self):
        self.portal_type = ''

class TestSubscriptionsTool(unittest.TestCase):
    """Test Subscriptions Tool

    This class tests the subscriptions tool :
     - Fixtures
     - Default settings
     - Initialization
     - ZMI
     - Misc API
    """

    subscriptions_tool = SubscriptionsTool()

    def beforeTearDown(self):
        # XXX
        pass

    def testSubscriptionsToolFixtures(self):
        #
        # Test subscriptions tool fixtures
        #
        self.assertNotEqual(self.subscriptions_tool, None)
        self.assertEqual(self.subscriptions_tool.id,
                         'portal_subscriptions')
        self.assertEqual(self.subscriptions_tool.meta_type,
                         'Subscriptions Tool')

    def testSubscriptionsToolGlobalIds(self):
        #
        # Test Subscriptions tool global ids
        #
        stool = self.subscriptions_tool
        self.assertEqual(stool.getSubscriptionContainerId(),
                         SUBSCRIPTION_CONTAINER_ID)
        self.assertEqual(stool.getExplicitRecipientsRuleId() ,
                         EXPLICIT_RECIPIENTS_RULE_ID)
        self.assertEqual(stool.getMailNotificationRuleObjectId(),
                         MAIL_NOTIFICATION_RULE_ID)

    ##def testSubscriptionsToolDefaultMessageElements(self):
    ##    #
    ##    # Test Subscriptions tool default message elements
    ##    #
    ##    default_message_title = self.subscriptions_tool.getDefaultMessageTitle()
    ##    self.assertNotEqual(default_message_title, None)
    ##    self.assertNotEqual(default_message_title, '')
    ##    self.assert_(isinstance(default_message_title, StringType))
    ##
    ##    default_message_body = self.subscriptions_tool.getDefaultMessageBody()
    ##    self.assertNotEqual(default_message_body, None)
    ##    self.assertNotEqual(default_message_body, '')
    ##    self.assert_(isinstance(default_message_body, StringType))
    ##
    ##    error_message_body = self.subscriptions_tool.getErrorMessageBody()
    ##    self.assertNotEqual(error_message_body, None)
    ##    self.assertNotEqual(error_message_body, '')
    ##    self.assert_(isinstance(error_message_body, StringType))

    def testSubscriptionsToolEventsRegistration(self):
        #
        # Test events registration in all registred context
        #

        context = Context()
        portal_types = self.subscriptions_tool.getContainerPortalTypes()
        self.assert_(isinstance(portal_types, ListType))

        for portal_type in portal_types:
            context.portal_type = portal_type
            events_in_context = self.subscriptions_tool.getEventsFromContext(
                context)
            self.assertNotEqual(events_in_context, {})
            self.assert_(isinstance(events_in_context, DictType))

    def testSubscriptionsToolRenderedPortalTypeRegistration(self):
        #
        # Tests adding some portal_types that have to be rendered at
        # notification time and then added to the notification email body
        #

        portal_type_ok = 'XXXX'
        portal_type_not_ok = ('XXXXXXXXXX',)
        currents = self.subscriptions_tool.getRenderedPortalTypes()
        initial_len = len(currents)

        self.assert_(isinstance(currents, ListType))

        self.assertEqual(self.subscriptions_tool.addRenderedPortalType(
            portal_type_ok),
                         1)
        new_currents = self.subscriptions_tool.getRenderedPortalTypes()
        new_len = len(new_currents)

        self.assertEqual(initial_len+1, new_len)

        self.assertEqual(self.subscriptions_tool.addRenderedPortalType(
            portal_type_not_ok),
                         0)

        currents = self.subscriptions_tool.getRenderedPortalTypes()
        self.assertEqual(len(currents), new_len)

    def testSubscriptionsToolRenderedEventsRegistration(self):
        #
        # Tests adding some events that have to be rendered at
        # notification time and then added to the notification email body
        #

        event_id_ok = 'XXXX'
        event_id_not_ok = ('XXXXXXXXXX',)
        currents = self.subscriptions_tool.getRenderedEvents()
        initial_len = len(currents)

        # This variables could be initialized
        # Just check in here if the structure hosting is a list
        self.assert_(isinstance(currents, ListType))

        self.assertEqual(
            self.subscriptions_tool.addRenderedEvent(event_id_ok),
            1)

        currents_plus = self.subscriptions_tool.getRenderedEvents()
        new_len = len(currents_plus)

        self.assertEqual(new_len, initial_len + 1)

        self.assertEqual(
            self.subscriptions_tool.addRenderedEvent(event_id_not_ok),
            0)
        new_currents = self.subscriptions_tool.getRenderedEvents()
        self.assertEqual(new_len, len(new_currents))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSubscriptionsTool))
    return suite

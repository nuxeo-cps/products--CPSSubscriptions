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
from Testing import ZopeTestCase

from Products.CMFCore.utils import getToolByName

from Products.CPSSubscriptions.SubscriptionsTool import \
     SUBSCRIPTION_CONTAINER_ID,\
     EXPLICIT_RECIPIENTS_RULE_ID,\
     MAIL_NOTIFICATION_RULE_ID

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


class Context:
    def __init__(self):
        self.portal_type = ''

def randomText(max_len=10):
    import random
    return ''.join(
        [chr(random.randint(32, 128)) for i in range(0, max_len)])

class TestSubscriptionsTool(CPSSubscriptionsTestCase.CPSSubscriptionsTestCase):
    """Test Subscriptions Tool

    This class tests the subscriptions tool :
     - Fixtures
     - Default settings
     - Initialization
     - ZMI
     - Misc API
    """

    def afterSetUp(self):
        self.login('root')
        self.portal.REQUEST.SESSION = {}
        self.portal.REQUEST.form = {}

        self.subscriptions_tool = getToolByName(self.portal,
                                                'portal_subscriptions')

    def beforeTearDown(self):
        self.logout()

    def testSubscriptionsToolFixtures(self):

        #
        # Test subscriptions tool fixtures
        #

        self.assertNotEqual(self.subscriptions_tool, None)
        self.assertEqual(self.subscriptions_tool.id,
                         'portal_subscriptions')
        self.assertEqual(self.subscriptions_tool.meta_type,
                         'Subscriptions Tool')

    def testSubscriptionsToolAttributes(self):

        #
        # Test Subscriptions tool attributes
        #

        # Default Attributes
        self.assertEqual(getattr(self.subscriptions_tool,
                                 'notify_hidden_object'), 0)

        # The following had been initialize with default values or some values
        # had been defined by users already

        self.assertNotEqual(getattr(self.subscriptions_tool,
                                    'mapping_context_events'), {})
        self.assertNotEqual(getattr(self.subscriptions_tool,
                                    'mapping_event_email_content'), {})

        # Default mail template elements
        self.assertNotEqual(getattr(self.subscriptions_tool,
                                    'event_default_email_title'), '')
        self.assertNotEqual(getattr(self.subscriptions_tool,
                                    'event_default_email_body'), '')

        # Error message not yet initialized at this stage
        self.assertEqual(getattr(self.subscriptions_tool,
                                 'event_error_email_body'), '')

    def testSubscriptionsToolGlobalIds(self):

        #
        # Test Subscriptions tool global ids
        #

        self.assertEqual(self.subscriptions_tool.getSubscriptionContainerId(),
                         SUBSCRIPTION_CONTAINER_ID)
        self.assertEqual(self.subscriptions_tool.getExplicitRecipientsRuleId() ,
                         EXPLICIT_RECIPIENTS_RULE_ID)
        self.assertEqual(
            self.subscriptions_tool.getMailNotificationRuleObjectId(),
            MAIL_NOTIFICATION_RULE_ID)

    def testSubscriptionsToolDefaultMessageElements(self):

        #
        # Test Subscriptions tool default message elements
        #

        default_message_title = self.subscriptions_tool.getDefaultMessageTitle()
        self.assertNotEqual(default_message_title, None)
        self.assertNotEqual(default_message_title, '')
        self.assertEqual(isinstance(default_message_title, StringType), 1)

        default_message_body = self.subscriptions_tool.getDefaultMessageBody()
        self.assertNotEqual(default_message_body, None)
        self.assertNotEqual(default_message_body, '')
        self.assertEqual(isinstance(default_message_body, StringType), 1)

        error_message_body = self.subscriptions_tool.getErrorMessageBody()
        self.assertNotEqual(error_message_body, None)
        self.assertNotEqual(error_message_body, '')
        self.assertEqual(isinstance(error_message_body, StringType), 1)

    def testSubscriptionsToolEventsRegistration(self):

        #
        # Test events registration in all registred context
        #

        context = Context()
        portal_types = self.subscriptions_tool.getContainerPortalTypes()
        self.assertEqual(isinstance(portal_types, ListType), 1)

        for portal_type in portal_types:
            context.portal_type = portal_type
            events_in_context = self.subscriptions_tool.getEventsFromContext(
                context)
            self.assertNotEqual(events_in_context, {})
            self.assertEqual(isinstance(events_in_context, DictType), 1)

    def testSubscriptionsToolRenderedPortalTypeRegistration(self):

        #
        # Tests adding some portal_types that have to be rendered at
        # notification time and then added to the notification email body
        #

        portal_type_ok= 'XXXX'
        portal_type_not_ok = ('XXXXXXXXXX',)
        currents = self.subscriptions_tool.getRenderedPortalTypes()
        self.assertEqual(currents, [])

        self.assertEqual(self.subscriptions_tool.addRenderedPortalType(
            portal_type_ok),
                         1)
        currents = self.subscriptions_tool.getRenderedPortalTypes()
        self.assertEqual(currents, [portal_type_ok])

        self.assertEqual(self.subscriptions_tool.addRenderedPortalType(
            portal_type_not_ok),
                         0)
        currents = self.subscriptions_tool.getRenderedPortalTypes()
        self.assertEqual(currents, [portal_type_ok])

    def testSubscriptionsToolRenderedEventsRegistration(self):

        #
        # Tests adding some events that have to be rendered at
        # notification time and then added to the notification email body
        #

        event_id_ok= 'XXXX'
        event_id_not_ok = ('XXXXXXXXXX',)
        currents = self.subscriptions_tool.getRenderedEvents()
        self.assertEqual(currents, [])

        self.assertEqual(self.subscriptions_tool.addRenderedEvent(
            event_id_ok),
                         1)
        currents = self.subscriptions_tool.getRenderedEvents()
        self.assertEqual(currents, [event_id_ok])

        self.assertEqual(self.subscriptions_tool.addRenderedEvent(
            event_id_not_ok),
                         0)
        currents = self.subscriptions_tool.getRenderedEvents()
        self.assertEqual(currents, [event_id_ok])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSubscriptionsTool))
    return suite

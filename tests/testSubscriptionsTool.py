# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Julien Anguenot <anguenot@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

import os
import sys

import unittest
import CPSSubscriptionsTestCase

from Products.CPSSubscriptions import SubscriptionsTool

class TestSubscriptionsTool(
    CPSSubscriptionsTestCase.CPSSubscriptionsTestCase):
    """Test Subscriptions Tool
    """

    def afterSetUp(self):
        self.login('manager')
        self._stool = self.portal.portal_subscriptions

    def testSubscriptionsToolFixtures(self):
        self.assertNotEqual(self._stool, None)
        self.assertEqual(
            self._stool.id, 'portal_subscriptions')
        self.assertEqual(
            self._stool.meta_type, 'Subscriptions Tool')

    def testSubscriptionsToolGlobalIds(self):
        self.assertEqual(
            self._stool.getSubscriptionContainerId(),
            SubscriptionsTool.SUBSCRIPTION_CONTAINER_ID)
        self.assertEqual(
            self._stool.getExplicitRecipientsRuleId() ,
            SubscriptionsTool.EXPLICIT_RECIPIENTS_RULE_ID)
        self.assertEqual(
            self._stool.getMailNotificationRuleObjectId(),
            SubscriptionsTool.MAIL_NOTIFICATION_RULE_ID)

    def testSubscriptionsToolEventsRegistration(self):

        #
        # Test events registration in all registred context
        #

        class Context:
            def __init__(self):
                self.portal_type = ''

        context = Context()
        portal_types = self._stool.getContainerPortalTypes()
        self.assert_(isinstance(portal_types, list))

        for portal_type in portal_types:
            context.portal_type = portal_type
            events_in_context = self._stool.getEventsFromContext(context)
            self.assertNotEqual(events_in_context, {})
            self.assert_(isinstance(events_in_context, dict))

    def testSubscriptionsToolRenderedPortalTypeRegistration(self):

        #
        # Tests adding some portal_types that have to be rendered at
        # notification time and then added to the notification email body
        #

        portal_type_ok = 'XXXX'
        portal_type_not_ok = ('XXXXXXXXXX',)
        currents = self._stool.getRenderedPortalTypes()
        initial_len = len(currents)

        self.assert_(isinstance(currents, list))

        self.assertEqual(self._stool.addRenderedPortalType(portal_type_ok), 1)
        new_currents = self._stool.getRenderedPortalTypes()
        new_len = len(new_currents)
        self.assertEqual(initial_len+1, new_len)
        self.assertEqual(
            self._stool.addRenderedPortalType(portal_type_not_ok), 0)

        currents = self._stool.getRenderedPortalTypes()
        self.assertEqual(len(currents), new_len)

    def testSubscriptionsToolRenderedEventsRegistration(self):

        #
        # Tests adding some events that have to be rendered at
        # notification time and then added to the notification email body
        #

        event_id_ok = 'XXXX'
        event_id_not_ok = ('XXXXXXXXXX',)
        currents = self._stool.getRenderedEvents()
        initial_len = len(currents)

        # This variables could be initialized
        # Just check in here if the structure hosting is a list
        self.assert_(isinstance(currents, list))

        self.assertEqual(
            self._stool.addRenderedEvent(event_id_ok), 1)

        currents_plus = self._stool.getRenderedEvents()
        new_len = len(currents_plus)

        self.assertEqual(new_len, initial_len + 1)

        self.assertEqual(
            self._stool.addRenderedEvent(event_id_not_ok), 0)
        new_currents = self._stool.getRenderedEvents()
        self.assertEqual(new_len, len(new_currents))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSubscriptionsTool))
    return suite

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

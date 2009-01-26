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

from Acquisition import aq_parent, aq_inner

import CPSSubscriptionsTestCase

from Products.CPSSubscriptions import SubscriptionsTool

class UnitTestSubscriptionsTool(unittest.TestCase):
    """For quick running unit tests."""

    def setUp(self):
        self.stool = SubscriptionsTool.SubscriptionsTool()
        self.stool.manage_changeProperties(
            render_content_for_portal_types=(
                'File', 'News Item:evt1', 'Document:', 'Note:create, publish'))
        self.stool.manage_changeProperties(
            render_content_for_events=('wf_create', 'wf_publish:News Item,Gig'))
    
    def testPostProcessing(self):
        _marker_all = SubscriptionsTool._marker_all
        self.assertEquals(self.stool.render_content_for_portal_types_c, 
                          {'File': _marker_all,
                           'News Item': ('evt1',),
                           'Document': _marker_all,
                           'Note': ('create', 'publish'),
                           })
        self.assertEquals(self.stool.render_content_for_events_c, 
                          {'wf_publish': ('News Item', 'Gig'),
                           'wf_create': _marker_all,
                           })

    def testShouldRender(self):
        shouldRender = self.stool.shouldRender
        self.assertFalse(shouldRender(None, 'wf_create'))

        class FakeContent:
            pass
        content = FakeContent()
        
        content.portal_type = 'News Item'
        self.assertFalse(shouldRender(content, 'unknown_event'))
        self.assertTrue(shouldRender(content, 'wf_publish'))
        self.assertTrue(shouldRender(content, 'wf_create'))
        self.assertTrue(shouldRender(content, 'evt1'))

        content.portal_type = 'File'
        self.assertTrue(shouldRender(content, 'unknown_event'))

        content.portal_type = 'Unknown Type'
        self.assertTrue(shouldRender(content, 'wf_create'))
                     

class TestSubscriptionsTool(
    CPSSubscriptionsTestCase.CPSSubscriptionsTestCase):
    """Test Subscriptions Tool
    """

    def afterSetUp(self):
        self.login('manager')
        self._stool = self.portal.portal_subscriptions
        self.utool = self.portal.portal_url


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

        self.assert_(isinstance(currents, tuple))

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
        # Just check in here if the structure hosting is a sequence
        self.assert_(isinstance(currents, tuple))

        self.assertEqual(self._stool.addRenderedEvent(event_id_ok), 1)

        currents_plus = self._stool.getRenderedEvents()
        new_len = len(currents_plus)

        self.assertEqual(new_len, initial_len + 1)

        self.assertEqual(self._stool.addRenderedEvent(event_id_not_ok), 0)
        new_currents = self._stool.getRenderedEvents()
        self.assertEqual(new_len, len(new_currents))


    def test_getSubscriptionContainerFromContext_folder(self):
        id_ = self.portal.workspaces.invokeFactory('Workspace', 'ws')
        ws = getattr(self.portal.workspaces, id_)
        container = self._stool.getSubscriptionContainerFromContext(ws)
        print container.absolute_url()
        self.assertEqual(ws, aq_parent(aq_inner(container)))


    def test_getSubscriptionContainerFromContext_document(self):
        id_ = self.portal.workspaces.invokeFactory('File', 'file')
        file = getattr(self.portal.workspaces, id_)
        container = self._stool.getSubscriptionContainerFromContext(file)
        self.assertEqual(self.portal.workspaces, aq_parent(aq_inner(container)))


    def test_getSubscriptionContainerFromContext_nonfolderish(self):
        # http://svn.nuxeo.org/trac/pub/ticket/1158
        if 'CPS Calendar' not in self.portal.portal_types.objectIds():
            return
        id_ = self.portal.workspaces.invokeFactory('Workspace', 'calendars')
        calendars = getattr(self.portal.workspaces, id_)
        id_calendar = calendars.invokeFactory('CPS Calendar', 'calendar')
        calendar = getattr(calendars, id_calendar)

        container = self._stool.getSubscriptionContainerFromContext(
            calendar)
        self.assertEqual(calendars, aq_parent(aq_inner(container)))



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UnitTestSubscriptionsTool))
    suite.addTest(unittest.makeSuite(TestSubscriptionsTool))
    return suite

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

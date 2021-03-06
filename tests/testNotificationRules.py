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

import unittest

import transaction
from Acquisition import aq_parent, aq_inner
from OFS.SimpleItem import SimpleItem

from Products.CPSSubscriptions.Notifications import NotificationRule

from CPSSubscriptionsTestCase import CPSSubscriptionsTestCase

class TestBaseNotificationRule(CPSSubscriptionsTestCase):

    def afterSetUp(self):
        CPSSubscriptionsTestCase.afterSetUp(self)
        self.login('manager')
        self._stool = self.portal.portal_subscriptions
        # Max recipients per mail notification at a time.
        # 20 is the default one.
        self._stool.max_recipients_per_notification = 3

    def beforeTearDown(self):
        self.logout()

class TestNotificationRule(TestBaseNotificationRule):

    # Test the base notification rule behavior when standlone

    def afterSetUp(self):
        self._notification = NotificationRule(id='notification')

    def test_getSubscriptionContainer(self):
        self.assertEqual(None, self._notification.getSubscriptionContainer())

    def test_getParentSusbcription(self):
        self.assertEqual(None, self._notification.getParentSubscription())

    def test_notifyRecipients(self):
        self.assertRaises(
            NotImplementedError, self._notification.notifyRecipients)

class TestMailNotificationRule(TestBaseNotificationRule):

    def afterSetUp(self):
        TestBaseNotificationRule.afterSetUp(self)
        # Create a susbcription container at the root of the portal
        # for the tests
        self.portal.manage_addProduct[
            'CPSSubscriptions'].addSubscriptionContainer()
        container = getattr(
            self.portal, self._stool.getSubscriptionContainerId())
        # Add a subscription object
        subscription = container.addSubscription('fake_event_id')
        # Get the default notification rule for the subscription
        self._notification = subscription.getNotificationRules()[0]

    def test_getSubscriptionContainer(self):
        self.assertEqual(
            self._notification.getSubscriptionContainer(),
            getattr(self.portal, self._stool.getSubscriptionContainerId()))
        self.assertEqual(
            self._notification.getSubscriptionContainer().portal_type,
            'CPS PlaceFull Subscription Container')

    def test_getParentSusbcription(self):
        self.assertEqual(aq_parent(aq_inner(self._notification)),
                         self._notification.getParentSubscription())
        self.assertEqual(
            self._notification.getParentSubscription().portal_type,
            'CPS Subscription Configuration')

    def test_notifyRecipients_lesser_than_max_recipients(self):

        # Notify a list of emails < to max recipients
        # We should get only one email as a result
        emails = ['ja@nuxeo.com', 'contact@nuxeo.com']
        self._stool.mapping_context_events = {'Portal':
                                              {'fake_event_id': 'Yo'}}
        self._stool.mapping_event_email_content = {'fake_event_id': 'ha'}
        self._notification.notifyRecipients(
            'fake_event_id', self.portal.sections, emails=emails)
        self.assertEqual(len(self._mh.mail_log), 1)
        mail = self._mh.mail_log[0]
        self.assertEqual(mail['bcc'], ','.join(emails))

        self._mh.clearLog()

    def test_notifyRecipients_postponed(self):

        # Notify a list of emails < to max recipients
        # We should get only one email as a result
        emails = ['ja@nuxeo.com', 'contact@nuxeo.com']
        sections = self.portal.sections
        cont = self._stool.getSubscriptionContainerFromContext(sections)
        cont.updateUserMode('ja@nuxeo.com', 'postponed')
        self._stool.mapping_context_events = {'Portal':
                                              {'fake_event_id': 'Yo'}}
        self._stool.mapping_event_email_content = {'fake_event_id': 'ha'}

        self._notification.notifyRecipients(
            'fake_event_id', sections, emails=emails)
        self.assertEqual(len(self._mh.mail_log), 1)
        mail = self._mh.mail_log[0]
        self.assertEqual(mail['bcc'], 'contact@nuxeo.com') # ja is postponed
        self._mh.clearLog()

    def test_notifyRecipients_greater_than_max_recipients(self):

        # Notify a list of emails > max_recipients
        # We should get 2 mails
        emails = ['ja@nuxeo.com', 'contact@nuxeo.com',
                  'bob@nuxeo.com', 'jack@nuxeo.com']
        self._stool.mapping_context_events = {'Portal':
                                              {'fake_event_id': 'Yo'}}
        self._stool.mapping_event_email_content = {'fake_event_id': 'ha'}
        self._notification.notifyRecipients(
            'fake_event_id', self.portal.sections, emails=emails)
        self.assertEqual(len(self._mh.mail_log), 2)
        mail = self._mh.mail_log[0]
        self.assertEqual(
            mail['bcc'], ','.join(['ja@nuxeo.com', 'contact@nuxeo.com',
                                   'bob@nuxeo.com']))
        mail = self._mh.mail_log[1]
        self.assertEqual(mail['bcc'], ','.join(['jack@nuxeo.com']))

        self._mh.clearLog()

    def test_notifyWelcomeSubscription(self):
        email = 'bob@nuxeo.com'
        event_id = 'fake_event_id'
        self.portal._setObject('item', SimpleItem('item'))
        object_ = getattr(self.portal, 'item')
        context = object_
        self._notification.notifyWelcomeSubscription(
            event_id, object_, email, context)
        mail = self._mh.mail_log[0]
        self.assertEqual(mail['to'], 'bob@nuxeo.com')
        self.assert_(mail['message'])
        self._mh.clearLog()

    def test_notifyUnSubscribe(self):
        email = 'bob@nuxeo.com'
        event_id = 'fake_event_id'
        self.portal._setObject('item', SimpleItem('item'))
        object_ = getattr(self.portal, 'item')
        context = object_

        # Subscribe
        self._notification.notifyWelcomeSubscription(
            event_id, object_, email, context)
        mail = self._mh.mail_log[0]
        self.assertEqual(mail['to'], 'bob@nuxeo.com')
        self.assert_(mail['message'])
        self._mh.clearLog()

        # Unsubsribe
        self._notification.notifyUnSubscribe(
            event_id, object_, email, context)
        mail = self._mh.mail_log[0]
        self.assertEqual(mail['to'], 'bob@nuxeo.com')
        self.assert_(mail['message'])
        self._mh.clearLog()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNotificationRule))
    suite.addTest(unittest.makeSuite(TestMailNotificationRule))
    return suite

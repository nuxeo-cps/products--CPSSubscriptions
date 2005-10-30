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
import email
import unittest

from OFS.SimpleItem import SimpleItem
import transaction

import CPSSubscriptionsTestCase

from Products.CPSSubscriptions.Notifications import NotificationRule
from Products.CPSSubscriptions.Notifications import MailNotificationRule

class DummyMailHost(SimpleItem):
    """Host that stores the sent mails in a list

    The list can then be inspected. This way you can see who got notified.
    """

    mail_log = []

    def clearLog(self):
        self.mail_log = []

    def send(self, raw_message):
        message = email.message_from_string(raw_message)
        mfrom = message['From']
        mto = message['To']
        subject = message['Subject']
        bcc = message['Bcc']
        self.mail_log.append({'from': mfrom, 'to': mto, 'message': message,
                              'subject': subject, 'bcc': bcc})

class TestBaseNotificationRule(
    CPSSubscriptionsTestCase.CPSSubscriptionsTestCase):

    def afterSetUp(self):
        self.login('manager')
        self._setupDummyMailHost()
        self._stool = self.portal.portal_subscriptions
        # Max recipients per mail notification at a time.
        # 20 is the default one.
        self._stool.max_recipients_per_notification = 3

    def _setupDummyMailHost(self):
        # Set up the dummy mailhost
        self.portal._delObject('MailHost')
        self.portal._setObject('MailHost', DummyMailHost())
        self._mh = self.portal.MailHost
        # Get rid of any pending notifications
        transaction.commit()
        self._mh.clearLog()

    def beforeTearDown(self):
        self.logout()

class TestNotificationRule(TestBaseNotificationRule):

    def test_notifyRecipients(self):
        nr = NotificationRule(id='fake')
        self.assertRaises(NotImplementedError, nr.notifyRecipients)

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

    def test_notifyRecipients_lesser_than_max_recipients(self):

        # Notify a list of emails < to max recipients
        # We should get only one email as a result
        emails = ['ja@nuxeo.com', 'contact@nuxeo.com']
        self._notification.notifyRecipients(
            'fake_event_id', self.portal, emails=emails)
        self.assertEqual(len(self._mh.mail_log), 1)
        mail = self._mh.mail_log[0]
        self.assertEqual(mail['bcc'], ','.join(emails))
        
        self._mh.clearLog()

    def test_notifyRecipients_greater_than_max_recipients(self):

        # Notify a list of emails > max_recipients
        # We should get 2 mails
        emails = ['ja@nuxeo.com', 'contact@nuxeo.com',
                  'bob@nuxeo.com', 'jack@nuxeo.com']
        self._notification.notifyRecipients(
            'fake_event_id', self.portal, emails=emails)
        self.assertEqual(len(self._mh.mail_log), 2)
        mail = self._mh.mail_log[0]
        self.assertEqual(
            mail['bcc'], ','.join(['ja@nuxeo.com', 'contact@nuxeo.com',
                                   'bob@nuxeo.com']))
        mail = self._mh.mail_log[1]
        self.assertEqual(mail['bcc'], ','.join(['jack@nuxeo.com']))

        self._mh.clearLog()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNotificationRule))
    suite.addTest(unittest.makeSuite(TestMailNotificationRule))
    return suite

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

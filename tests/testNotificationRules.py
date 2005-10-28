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

from Products.CPSSubscriptions.EventManager import get_event_manager
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
        print raw_message
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

    def test_notifyRecipients(self):

        subtool = self.portal.portal_subscriptions
        
        # Create a susbcription container
        self.portal.manage_addProduct[
            'CPSSubscriptions'].addSubscriptionContainer()
        container = getattr(
            self.portal, subtool.getSubscriptionContainerId())
        # Add a subscription
        subscription = container.addSubscription('fake_event_id')
        # Get the default notification rule
        notification = subscription.getNotificationRules()[0]

        # Notify a list of emails
        emails = ['ja@nuxeo.com', 'contact@nuxeo.com']
        notification.notifyRecipients('fake_event_id', self.portal, emails=emails)
        self.assertEqual(len(self._mh.mail_log), 1)
        mail = self._mh.mail_log[0]
        self.assertEqual(mail['bcc'], ','.join(emails))
        
        # Since CPS-3.3.x we now need to force the subscription tool
        # to send the mails by committing the transaction.
        em = get_event_manager()
        em()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNotificationRule))
    suite.addTest(unittest.makeSuite(TestMailNotificationRule))
    return suite

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

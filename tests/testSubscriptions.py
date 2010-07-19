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

class TestSubscriptions(
    CPSSubscriptionsTestCase.CPSSubscriptionsTestCase):

    def afterSetUp(self):
        self.login('manager')
        subtool = self.portal.portal_subscriptions
        
        # Create a susbcription container
        self.portal.manage_addProduct[
            'CPSSubscriptions'].addSubscriptionContainer()
        self._container = getattr(
            self.portal, subtool.getSubscriptionContainerId())
        # Add a subscription
        self._subscription = self._container.addSubscription('fake_event_id')

        # Get the explicit recipient rules
        self._explicit = self._subscription.getRecipientsRules(
            recipients_rule_type='Explicit Recipients Rule')[0]

    def test_importEmailsSubscribersListOK(self):

        list_ = ['ja@nuxeo.com', 'fg@nuxeo.com']
        self._explicit.importEmailsSubscriberList(list_)
        self.assertEqual(self._explicit.getSubscriberEmails(), list_)

    def test_importEmailsSubscribersListNotOK(self):

        # Using directly the API. No control on emails

        list_ = ['ja@nuxeo.com', 'fg@nuxeo.com', 'incorrect']
        self._explicit.importEmailsSubscriberList(list_)
        self.assertEqual(self._explicit.getSubscriberEmails(),
                         ['ja@nuxeo.com', 'fg@nuxeo.com'])

    def beforeTearDown(self):
        self.logout()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSubscriptions))
    return suite

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

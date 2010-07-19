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
"""Test the subscription container
"""

import unittest
import CPSSubscriptionsTestCase

from Products.CPSSubscriptions.SubscriptionContainer import \
     SubscriptionContainer
from Products.CPSSubscriptions.Subscription import Subscription

class TestSubscriptionContainer(
    CPSSubscriptionsTestCase.CPSSubscriptionsTestCase):

    def afterSetUp(self):
        self.login('manager')

    def beforeTearDown(self):
        self.logout()

    def test_fixtures(self):

        container = SubscriptionContainer('subc')
        self.assert_(isinstance(container, SubscriptionContainer))
        self.assertEqual(container.user_modes, {})

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

    def test_UserMode(self):

        subtool = self.portal.portal_subscriptions
        container = subtool.getSubscriptionContainerFromContext(
            self.portal.workspaces,
            force_local_creation=True,
           )
        self.assertEqual(container.user_modes, {})
        container.updateUserMode('bob@nuxeo.com', 'mode_daily')
        self.assertEqual(container.user_modes, {'bob@nuxeo.com':'mode_daily'})
        self.assertEqual(container.getUserMode('bob@nuxeo.com'), 'mode_daily')

    def test_PermissionSettingsAfterCreation(self):
        subtool = self.portal.portal_subscriptions
        container = subtool.getSubscriptionContainerFromContext(
            self.portal.workspaces,
            force_local_creation=True,
           )
        self.assert_('Authenticated' in container._Can_subscribe_Permission)

    def test_userMode_ZMI_changed(self):

        subtool = self.portal.portal_subscriptions
        container = subtool.getSubscriptionContainerFromContext(
            self.portal.workspaces,
            force_local_creation=True,
            )
        self.assertEqual(container.user_modes, {})
        container.user_modes = str({})
        # should not fail. The attr will be converted.
        self.assertEqual(
            container.getUserMode('bob@nuxeo.com'), 'mode_real_time')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSubscriptionContainer))
    return suite

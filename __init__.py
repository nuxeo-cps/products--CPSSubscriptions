# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2004 CGEY <http://cgey.com>
# Copyright (c) 2004 Ministère de L'intérieur (MISILL)
#               <http://www.interieur.gouv.fr/>
# Authors : Julien Anguenot <ja@nuxeo.com>
#           Florent Guillaume <fg@nuxeo.com>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# $Id$

__author__ = "Julien Anguenot <mailto:ja@nuxeo.com>"

""" CPS Subscriptions component

This component provides notifications and subscribtions for CPS3.
"""

from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import AddPortalContent,\
     ModifyPortalContent

import SubscriptionsTool
import SubscriptionContainer
import Subscription
import RecipientsRules
import Notifications
import NotificationMessageBody

#
# Recipients Rules
#

recipientsRulesClasses = ( RecipientsRules.ExplicitRecipientsRule,
                           RecipientsRules.RoleRecipientsRule,
                           RecipientsRules.WorkflowImpliedRecipientsRule,)

recipRulesConstructors = ( RecipientsRules.addExplicitRecipientsRule,
                           RecipientsRules.addRoleRecipientsRule,
                           RecipientsRules.addWorkflowImpliedRecipientsRule,)

#
# Notification Types
#

notificationsClasses = ( Notifications.MailNotificationRule,
                         NotificationMessageBody.NotificationMessageBody,)

notificationsConstructors = ( Notifications.addMailNotificationRule,
                              NotificationMessageBody.addNotificationMessageBody,)

#
# Subscription Tool
#

tools = ( SubscriptionsTool.SubscriptionsTool,)

registerDirectory('skins', globals())

def initialize(registar):
    """Initalization of CPSSubscriptions components
    """

    # Place Full Subscription Container
    registar.registerClass(\
        SubscriptionContainer.SubscriptionContainer,
        permission=AddPortalContent,
        constructors=(\
        SubscriptionContainer.addSubscriptionContainer, ))

    # Subscription object
    registar.registerClass(Subscription.Subscription,
                           permission=ModifyPortalContent,
                           constructors=(Subscription.addSubscription,))

    # Computed Recipients Rules
    registar.registerClass(RecipientsRules.ComputedRecipientsRule,
                           permission=ModifyPortalContent,
                           constructors=(RecipientsRules.addComputedRecipientsRuleForm,
                                         RecipientsRules.addComputedRecipientsRule,))

    # Recipients Rules
    ContentInit(
        'CPS Subscriptions Elements',
        content_types = recipientsRulesClasses + \
        notificationsClasses,
        permission = AddPortalContent,
        extra_constructors = recipRulesConstructors + \
        notificationsConstructors,).initialize(registar)

    # Portal Subscriptions Tool
    ToolInit(
        'CPS Subsriptions Tool',
        tools = tools,
        product_name = 'CPSSubscriptions',
        icon = 'tool.gif',).initialize(registar)

# Copyright (C) 2003 Nuxeo SARL <http://nuxeo.com>
# Copyright (C) 2003 CGEY <http://cgey.com>
# Copyright (c) 2003 Ministère de L'intérieur (MISILL)
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

""" Subscriptions Tool

Defines the Subscriptions Tool class
"""

from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import UniqueObject

from zLOG import LOG, DEBUG

##############################################################

## GLOBAL IDS

SUBSCRIPTION_CONTAINER = '.cps_subscriptions'
EXPLICIT_RECIPIENTS_RULE_ID = 'explicit__recipients_rule'
MAIL_NOTIFICATION_RULE_ID = 'mail__notification_rule'

##############################################################

class SubscriptionsTool(UniqueObject, Folder):
    """Subscriptions Tool

    portal_subcriptions is the central tool with the necessary methods to query
    the subscriptions and execute them.

    The subscriptions are looked up locally in a .cps_subscriptions folder in
    the object.
    """

    id = 'portal_subscriptions'
    meta_type = 'Subscriptions Tool'

    security = ClassSecurityInfo()

    security.declarePublic("getSubscriptionContainerId")
    def getSubscriptionContainerId(self):
        """ Returns the default id for subscription containers

        .cps_subscriptions by default
        """
        return SUBSCRIPTION_CONTAINER

    security.declarePublic("getExplicitRecipientsRuleId")
    def getExplicitRecipientsRuleId(self):
        """ Returns an in use id.

        Id in use for the ExplicitRecipientsRule object
        """
        return EXPLICIT_RECIPIENTS_RULE_ID

    security.declarePublic("getMailNotificationRuleObjectId")
    def getMailNotificationRuleObjectId(self):
        """ Returns an in use id.

        Id in use for the MailNoticationRule object.
        """
        return MAIL_NOTIFICATION_RULE_ID

    security.declarePrivate('notify_event')
    def notify_event(self, event_type, object, infos):
        """Standard event hook.

        Get the applicable subscriptions. Sends the event to the
        subscriptions.

        For workflow events, infos must contain the additional
        keyword arguments passed to the transition.
        """

        subscriptions = self.getSubscriptionsFor(event_type,
                                                 object,
                                                 infos)
        for subscription in subscriptions:
            if subscription.isInterestedInEvent(event_type, object, infos):
                subscription.sendEvent(event_type, object, infos)

    security.declarePublic("getSubscriptionsFor")
    def getSubscriptionsFor(self, event_type, object, infos=None):
        """Get the subscriptions applicable for this event.

        Some of the parameters may be None to get all subscriptions.
        """

        subscriptions = []
        subscriptionContainer = getattr(object,
                                     self.getSubscriptionContainerId(), 0)
        if subscriptionContainer:
            subscriptions += subscriptionContainer.getSubscriptions()
            subscriptions = [x for x in subscriptions \
                             if 'subscription__'+event_type == x.id]
        return subscriptions

    security.declarePublic("getRecipientsFor")
    def getRecipientsFor(self, event_type='', object=None, infos={}):
        """ Get all the recipients computed from all the subscriptions
        found.

        The black list parameter will pass within the infos parameter.
        """
        recipients = {}
        if event_type:
            subscriptions = self.getSubscriptionsFor(event_type, object, infos)
        else:
            events = self.getEventTypesFromContext() # skins
            subscriptions = []
            for event in events:
                subscriptions += self.getSubscriptionsFor(event, object, infos)
        for subscription in subscriptions:
            if subscription.isInterestedInEvent(event_type, object, infos):
                for pt_recipient_rule in subscription.getRecipientsRules():
                    pt_recipients = pt_recipient_rule.getRecipients(event_type,
                                                                    object,
                                                                    infos)
                    LOG("YYYYY", DEBUG, pt_recipients)
                    for pt_recipient in pt_recipients.keys():
                        recipients[pt_recipient] = pt_recipients[pt_recipient]
        return recipients

InitializeClass(SubscriptionsTool)

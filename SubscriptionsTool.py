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
from Acquisition import aq_base, aq_parent, aq_inner

from Products.CMFCore.utils import UniqueObject

from Subscription import Subscription

from zLOG import LOG, DEBUG

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

    def getSubscriptionId(self):
        """ Returns the default id for subscription object

        .cps_subscriptions byt default
        """
        default_id = '.cps_subscriptions'
        return default_id


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
        recipients = {}
        for subscription in subscriptions:
            if subscription.isInterestedInEvent(event_type, object, infos):
                recipients_rules = subscription.getRecipientsRules()
                for recipients_rule in recipients_rules:
                    subscription_recipients = recipients_rule.getRecipients(\
                     event_type,
                     object,
                     infos)
                    for key in subscription_recipients.keys():
                        if key not in recipients.keys():
                            recipients[key] = subscription_recipients[key]

        LOG("############## ALL RECIPIENTS ###############", DEBUG, recipients)

        # XXX getting the nofication type and doing sthg now.

    def getSubscriptionsFor(self, event_type, object, infos=None):
        """Get the subscriptions applicable for this event.

        Some of the parameters may be None to get all subscriptions.
        """

        subscriptions = []
        subscriptionFolder = getattr(object,
                                     self.getSubscriptionId(), 0)
        if subscriptionFolder:
            subscriptions += subscriptionFolder.getSubscriptions()

            # XXX need to do sthg about the id.
            subscriptions = [x for x in subscriptions \
                             if 'subscription__'+event_type == x.id]
        return subscriptions

InitializeClass(SubscriptionsTool)

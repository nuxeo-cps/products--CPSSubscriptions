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
from Globals import InitializeClass, DTMLFile
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo


from Products.CMFCore.CMFCorePermissions import ManagePortal, ModifyPortalContent
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

    _properties = (
        {'id':'mapping_context_events',
         'type':'string', 'mode':'r', 'label':'Mapping context / events'},
        )

    mapping_context_events = {}

    ###################################################
    # ZMI
    ###################################################

    manage_options = (
        Folder.manage_options +
        ({'label': "Events", 'action': 'manage_events',},) +
        ())

    security.declareProtected(ManagePortal, 'manage_events')
    manage_events = DTMLFile('zmi/configureEvents', globals())


    def manage_addEventType(self, event_where, event_id, event_label, REQUEST=None):
        """ Adds a new event id in a given context
        """
        mapping_context_events = self.mapping_context_events
        if mapping_context_events.has_key(event_where):
            if not self.mapping_context_events[event_where].has_key(event_id):
                self.mapping_context_events[event_where][event_id] = event_label
        else:
            self.mapping_context_events[event_where] = {}
            self.mapping_context_events[event_where][event_id] = event_label
        self.mapping_context_events = mapping_context_events

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_events')

    ###################################################
    # SUBSCRIPTIONS TOOL API
    ###################################################

    #
    # ID's
    #

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

    #
    # ACCESSORS
    #

    security.declarePublic("getEventsFromContext")
    def getEventsFromContext(self, context=None):
        """ Returns events given a context.
        """
        if context is not None:
            context_portal_type = context.portal_type
            if self.mapping_context_events.has_key(context_portal_type):
                return self.mapping_context_events[context_portal_type]
            else:
                raise NotImplementedError
        return {}

    #
    # NOTIFICATIONS API
    #

    security.declarePrivate("notify_event")
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

        if object is None and infos.has_key('context'):
            object = infos['context']
        container = aq_parent(aq_inner(object))

        if event_type:
            subscriptions = self.getSubscriptionsFor(event_type, object, infos)
        else:
            events = self.getEventsFromContext(context=container)
            subscriptions = []
            for event in events.keys():
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

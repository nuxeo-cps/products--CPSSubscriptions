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

"""Subscriptions Tool

Defines the Subscriptions Tool class
"""

from OFS.Folder import Folder
from Globals import InitializeClass, DTMLFile
from Acquisition import aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import UniqueObject, getToolByName

from zLOG import LOG, DEBUG

##############################################################

# Global ids
SUBSCRIPTION_CONTAINER_ID = '.cps_subscriptions'
EXPLICIT_RECIPIENTS_RULE_ID = 'explicit__recipients_rule'
MAIL_NOTIFICATION_RULE_ID = 'mail__notification_rule'

##############################################################

class SubscriptionsTool(UniqueObject, Folder):
    """Subscriptions Tool

    portal_subcriptions is the central tool with the necessary methods
    to query the subscriptions and execute them.

    The subscriptions are looked up locally in a .cps_subscriptions folder in
    the object.
    """

    id = 'portal_subscriptions'
    meta_type = 'Subscriptions Tool'

    security = ClassSecurityInfo()

    _properties = (
        {'id': 'notify_hidden_object',
         'type': 'boolean', 'mode':'w',
         'label' : 'Notify hidden files'},
         {'id': 'event_default_email_title',
         'type':'string', 'mode':'r',
         'label':'Default email title'},
        {'id': 'event_default_email_body',
         'type':'text', 'mode':'r',
         'label':'Default email body'},
        {'id': 'event_error_email_body',
         'type' : 'text', 'mode':'r',
         'label': 'Error email body',},
        {'id': 'subscribe_confirm_email_title',
         'type' : 'string', 'mode':'r',
         'label': 'Subscribe Confirm Email Title',},
        {'id': 'subscribe_confirm_email_body',
         'type' : 'text', 'mode':'r',
         'label': 'Subscribe Confirm Email Body',},
        {'id': 'subscribe_welcome_email_title',
         'type' : 'string', 'mode':'r',
         'label': 'Subscribe Email Welcome Title',},
        {'id': 'subscribe_welcome_email_body',
         'type' : 'text', 'mode':'r',
         'label': 'Subscribe Email Welcome Body',},
        {'id': 'unsubscribe_email_title',
         'type' : 'string', 'mode':'r',
         'label': 'UnSubscribe Email Title',},
        {'id': 'unsubscribe_email_body',
         'type' : 'text', 'mode':'r',
         'label': 'UnSubscribe Email Body',},
        {'id': 'unsubscribe_confirm_email_title',
         'type' : 'string', 'mode':'r',
         'label': 'UnSubscribe Confirm Email Title',},
        {'id': 'unsubscribe_confirm_email_body',
         'type' : 'text', 'mode':'r',
         'label': 'UnSubscribe Confirm Email Body',},
        {'id':'mapping_context_events',
         'type':'string', 'mode':'r',
         'label':'Mapping context / events'},
        {'id': 'mapping_event_email_content',
         'type': 'string', 'mode': 'r',
         'label' : 'Mapping event email content'},
        )

    ###################################################
    # ZMI
    ###################################################

    manage_options = (
        {'label': "About",
         'action': 'about'
         },
        {'label': "Events and context / Add",
         'action': 'manage_events',
         },
        {'label': "Edit events content messages",
         'action': 'manage_edit_events',
         },
        ) + Folder.manage_options[2:4]

    security.declareProtected(ManagePortal, 'manage_events')
    manage_events = DTMLFile('zmi/configureEvents', globals())

    security.declareProtected(ManagePortal, 'about')
    about = DTMLFile('zmi/about_portal_subscriptions', globals())

    security.declareProtected(ManagePortal, 'manage_edit_events')
    manage_edit_events = DTMLFile('zmi/editEvents', globals())

    security.declareProtected(ManagePortal, 'manage_edit_event')
    manage_edit_event = DTMLFile('zmi/configureEvent', globals())

    def manage_editDefaultEventMessage(self,
                                       event_default_email_title,
                                       event_default_email_body,
                                       event_error_email_body,
                                       subscribe_confirm_email_body,
                                       subscribe_confirm_email_title,
                                       subscribe_welcome_email_body,
                                       subscribe_welcome_email_title,
                                       unsubscribe_email_title,
                                       unsubscribe_email_body,
                                       unsubscribe_confirm_email_title,
                                       unsubscribe_confirm_email_body,
                                       REQUEST=None):
        """Edit the default event email
        """
        self._p_changed = 1

        # No %(sthg)s in the error message. It's the purpose of that kind of
        # message.
        if '%' in event_error_email_body:
            event_error_email_body = event_error_email_body.replace('%', '')

        # Notifications
        self.event_default_email_title = event_default_email_title
        self.event_default_email_body = event_default_email_body
        self.event_error_email_body = event_error_email_body

        # Subscriptions
        self.subscribe_confirm_email_body = subscribe_confirm_email_body
        self.subscribe_confirm_email_title = subscribe_confirm_email_title
        self.subscribe_welcome_email_body = subscribe_welcome_email_body
        self.subscribe_welcome_email_title = subscribe_welcome_email_title

        # UnSubscriptions
        self.unsubscribe_email_body = unsubscribe_email_body
        self.unsubscribe_email_title = unsubscribe_email_title
        self.unsubscribe_confirm_email_body = unsubscribe_confirm_email_body
        self.unsubscribe_confirm_email_title = unsubscribe_confirm_email_title

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_edit_events')

    def manage_editEventMessage(self,
                                event_id,
                                event_email_title,
                                event_email_body,
                                subscribe_confirm_email_body='',
                                subscribe_confirm_email_title='',
                                subscribe_welcome_email_body='',
                                subscribe_welcome_email_title='',
                                unsubscribe_email_title='',
                                unsubscribe_email_body='',
                                unsubscribe_confirm_email_title='',
                                unsubscribe_confirm_email_body='',
                                REQUEST=None):
        """Edit a custom event message
        """
        self._p_changed = 1

        struct = [event_email_title,
                  event_email_body,
                  subscribe_confirm_email_title,
                  subscribe_confirm_email_body,
                  subscribe_welcome_email_title,
                  subscribe_welcome_email_body,
                  unsubscribe_email_title,
                  unsubscribe_email_body,
                  unsubscribe_confirm_email_title,
                  unsubscribe_confirm_email_body,]

        self.mapping_event_email_content[event_id] = struct

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_edit_events')


    def manage_addEventType(self, event_where, event_id, event_label, REQUEST=None):
        """ Adds a new event id in a given context
        """
        self._p_changed = 1

        mapping_context_events = self.mapping_context_events
        if mapping_context_events.has_key(event_where):
            if not self.mapping_context_events[event_where].has_key(event_id):
                self.mapping_context_events[event_where][event_id] = event_label
        else:
            self.mapping_context_events[event_where] = {}
            self.mapping_context_events[event_where][event_id] = event_label
        self.mapping_context_events = mapping_context_events

        self.mapping_event_email_content[event_id] = [
            self.getDefaultMessageTitle(),
            self.getDefaultMessageBody(),
            self.getSubscribeConfirmEmailTitle(),
            self.getSubscribeConfirmEmailBody(),
            self.getSubscribeWelcomeEmailTitle(),
            self.getSubscribeWelcomeEmailBody(),
            self.getUnSubscribeConfirmEmailTitle(),
            self.getUnSubscribeConfirmEmailBody(),
            self.getUnSubscribeEmailTitle(),
            self.getUnSubscribeEmailBody(),]

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_events')


    ###################################################
    # SUBSCRIPTIONS TOOL API
    ###################################################

    def __init__(self):
        """Initialization of default properties.

        Core attributs and default messages contents
        """
        # Core attrs
        self.notify_hidden_object = 0
        self.mapping_context_events = {}
        self.mapping_event_email_content = {}

        # Notifications
        self.event_default_email_title = ''
        self.event_default_email_body = ''
        self.event_error_email_body = ''


        # Subscriptions
        self.subscribe_confirm_email_title = ''
        self.subscribe_confirm_email_body = ''
        self.subscribe_welcome_email_title = ''
        self.subscribe_welcome_email_body = ''

        # UnSubscriptions
        self.unsubscribe_confirm_email_title = ''
        self.unsubscribe_confirm_email_body = ''
        self.unsubscribe_email_title = ''
        self.unsubscribe_email_body = ''

    ######################################################
    #####################################################

    security.declarePublic('getSubscriptionContainerId')
    def getSubscriptionContainerId(self):
        """ Returns the default id for subscription containers

        .cps_subscriptions by default
        """
        return SUBSCRIPTION_CONTAINER_ID

    security.declarePublic('getExplicitRecipientsRuleId')
    def getExplicitRecipientsRuleId(self):
        """ Returns an in use id.

        Id in use for the ExplicitRecipientsRule object
        """
        return EXPLICIT_RECIPIENTS_RULE_ID

    security.declarePublic('getMailNotificationRuleObjectId')
    def getMailNotificationRuleObjectId(self):
        """ Returns an in use id.

        Id in use for the MailNoticationRule object.
        """
        return MAIL_NOTIFICATION_RULE_ID

    ###########################################################
    ###########################################################

    security.declarePublic('getDefaultMessageTitle')
    def getDefaultMessageTitle(self, event_id=None):
        """Returns the default event message title.

        If event_id then look for the current title that applied
        to this given event.
        """
        if event_id is not None:
            if self.mapping_event_email_content.has_key(event_id):
                return self.mapping_event_email_content[event_id][0]
        else:
            if not self.event_default_email_title:
                # Init of the variable here.
                self.event_default_email_title = self.getMailTemplate()[
                    'mail_subject']
            return self.event_default_email_title

    security.declarePublic('getDefaultMessageBody')
    def getDefaultMessageBody(self, event_id=None):
        """Returns the default event message title

        If event_id then look for the current title that applied
        to this given event.
        """
        if event_id is not None:
            if self.mapping_event_email_content.has_key(event_id):
                return self.mapping_event_email_content[event_id][1]
        else:
            if not self.event_default_email_body:
                # Init of the variable here.
                self.event_default_email_body = self.getMailTemplate()[
                    'mail_body']
            return self.event_default_email_body

    security.declarePublic('getErrorMessageBody')
    def getErrorMessageBody(self, event_id=None):
        """Returns the error event message title

        Used especially when the user edited the body of the event
        but put wrong variable names.

        If event_id is specified then let's check if we get a custom
        one.
        """
        if event_id is not None:
            if self.mapping_event_email_content.has_key(event_id):
                return self.mapping_event_email_content[event_id][2]
        else:
            if not self.event_error_email_body:
                # Init of the variable here.
                self.event_error_email_body = self.getMailTemplate()[
                    'mail_error_body']
            return self.event_error_email_body

    security.declarePublic('getSubscribeConfirmEmailTitle')
    def getSubscribeConfirmEmailTitle(self, event_id=None):
        """Returns the subcribe confirmation email title

        If event_id is specified then let's check if we get a custom
        one for the given event.
        """
        # XXX event
        if not self.subscribe_confirm_email_title:
            # Init of the variable here.
            self.subscribe_confirm_email_title = self.getMailTemplate()[
                'subscribe_confirm_email_title']
        return self.subscribe_confirm_email_title

    security.declarePublic('getSubscribeConfirmEmailBody')
    def getSubscribeConfirmEmailBody(self, event_id=None):
        """Returns the subcribe confirmation email body

        If event_id is specified then let's check if we get a custom
        one for the given event.
        """
        # XXX event
        if not self.subscribe_confirm_email_body:
            # Init of the variable here.
            self.subscribe_confirm_email_body = self.getMailTemplate()[
                'subscribe_confirm_email_body']
        return self.subscribe_confirm_email_body

    security.declarePublic('getSubscribeWelcomeEmailTitle')
    def getSubscribeWelcomeEmailTitle(self, event_id=None):
        """Returns the subcribe welcome email title

        If event_id is specified then let's check if we get a custom
        one for the given event.
        """
        # XXX event
        if not self.subscribe_welcome_email_title:
            # Init of the variable here.
            self.subscribe_welcome_email_title = self.getMailTemplate()[
                'subscribe_welcome_email_title']
        return self.subscribe_welcome_email_title

    security.declarePublic('getSubscribeWelcomeEmailBody')
    def getSubscribeWelcomeEmailBody(self, event_id=None):
        """Returns the subcribe welcome email body

        If event_id is specified then let's check if we get a custom
        one for the given event.
        """
        # XXX event
        if not self.subscribe_welcome_email_body:
            # Init of the variable here.
            self.subscribe_welcome_email_body = self.getMailTemplate()[
                'subscribe_welcome_email_body']
        return self.subscribe_welcome_email_body

    security.declarePublic('getUnSubscribeEmailTitle')
    def getUnSubscribeEmailTitle(self, event_id=None):
        """Returns the unsubcribe email title

        If event_id is specified then let's check if we get a custom
        one for the given event.
        """
        # XXX event_id
        if not self.unsubscribe_email_title:
            # Init of the variable here.
            self.unsubscribe_email_title = self.getMailTemplate()[
                'unsubscribe_email_title']
        return self.unsubscribe_email_title

    security.declarePublic('getUnSubscribeEmailBody')
    def getUnSubscribeEmailBody(self, event_id=None):
        """Returns the unsubcribe email body

        If event_id is specified then let's check if we get a custom
        one for the given event.
        """
        # XXX event_id
        if not self.unsubscribe_email_body:
            # Init of the variable here.
            self.unsubscribe_email_body = self.getMailTemplate()[
                'unsubscribe_email_body']
        return self.unsubscribe_email_body

    security.declarePublic('getUnSubscribeConfirmEmailTitle')
    def getUnSubscribeConfirmEmailTitle(self, event_id=None):
        """Returns the unsubcribe confirm email title

        If event_id is specified then let's check if we get a custom
        one for the given event.
        """
        # XXX event_id
        if not self.unsubscribe_confirm_email_title:
            # Init of the variable here.
            self.unsubscribe_confirm_email_title = self.getMailTemplate()[
                'unsubscribe_confirm_email_title']
        return self.unsubscribe_confirm_email_title

    security.declarePublic('getUnSubscribeConfirmEmailBody')
    def getUnSubscribeConfirmEmailBody(self, event_id=None):
        """Returns the unsubcribe confirm email body

        If event_id is specified then let's check if we get a custom
        one for the given event.
        """
        # XXX event_id
        if not self.unsubscribe_confirm_email_body:
            # Init of the variable here.
            self.unsubscribe_confirm_email_body = self.getMailTemplate()[
                'unsubscribe_confirm_email_body']
        return self.unsubscribe_confirm_email_body

    #######################################################
    #######################################################

    security.declarePublic('getSubscriptablePortalTypes')
    def getSubscriptablePortalTypes(self):
        """Returns the possible subscriptable portal types
        """
        # XXX filtering on what ? lookup ?
        return self.mapping_context_events.keys()

    security.declarePublic('getEventsFromContext')
    def getEventsFromContext(self, context=None):
        """ Returns events given a context.
        """
        if context is not None:
            context_portal_type = context.portal_type
            if self.mapping_context_events.has_key(context_portal_type):
                return self.mapping_context_events[context_portal_type]
        return {}

    security.declarePublic('getContainerPortalTypes')
    def getContainerPortalTypes(self):
        """Get all portal types in when we can set notifications
        """
        return self.mapping_context_events.keys()

    security.declarePublic('getRecordedEvents')
    def getRecordedEvents(self):
        """Returns recorded events
        """
        return self.mapping_event_email_content.keys()

    #########################################################
    #########################################################

    security.declarePublic('getSusbcriptionContainerFromContext')
    def getSubscriptionContainerFromContext(self, context):
        """Returns a subscriptions container id.

        Lookup to find one through acquisition
        """
        container_id = self.getSubscriptionContainerId()
        return getattr(context, container_id, None)

    security.declarePrivate("notify_event")
    def notify_event(self, event_type, object, infos):
        """Standard event hook.

        Get the applicable subscriptions. Sends the event to the
        subscriptions.

        For workflow events, infos must contain the additional
        keyword arguments passed to the transition.
        """
        subscriptions = self.getSubscriptionsFor(event_type, object, infos)
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
            subscriptions = [x for x in subscriptions
                             if 'subscription__' + event_type == x.id]
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
                    for pt_recipient in pt_recipients.keys():
                        recipients[pt_recipient] = pt_recipients[pt_recipient]
        return recipients

    #############################################################
    #############################################################

    security.declarePublic('getAllSubscriptionsFor')
    def getAllSubscriptionsFor(self, email=None, context=None):
        """Returns all the subscriptions for a given member/email.

        Catalog research. getRecipients is indexed for the subscriptions
        container.

        Notice, anonymous user can as well check their subscriptions.
        """
        # XXX Implement for anonymous

        membership_tool = getToolByName(self, 'portal_membership')
        isAnonymousUser = membership_tool.isAnonymousUser()

        if not isAnonymousUser:
            member_id = membership_tool.getAuthenticatedMember().getMemberId()
            email = self.getMemberEmail(member_id)

        if not email:
            return []

        if context is not None:
            path = context.absolute_url()
        else:
            path = getToolByName(self, 'portal_url').getPortalPath()

        catalog = getToolByName(self, 'portal_catalog')
        portal_type = 'CPS PlaceFull Subscription Container'

        containers = catalog.searchResults({'portal_type':
                                            portal_type,
                                            'path':path,})

        subscriptions_list = []
        for container in containers:
            container_parent = aq_parent(aq_inner(container.getObject()))
            recipients = self.getRecipientsFor(
                infos={'context':container_parent})
            if email in recipients.keys():
                elt = {}
                elt['title'] = container_parent.title_or_id()
                if getattr(container_parent, 'getContent'):
                    doc = container_parent.getContent()
                    elt['description'] = doc.Description()
                else:
                    elt['description'] = container_parent.Description()
                elt['path'] = container_parent.absolute_url()
                subscriptions_list.append(elt)

        return subscriptions_list

    security.declarePublic('isSubscriberFor')
    def isSubscriberFor(self, event_id, context, email='', role_based=0):
        """Is a given member subscriber for a given email in the given context
        """

        subscriptions = self.getSubscriptionsFor(event_id, context)
        if not subscriptions:
            return 0

        subscription = subscriptions[0]

        membership_tool = getToolByName(self, 'portal_membership')
        isAno = membership_tool.isAnonymousUser()
        if not isAno:
            member = membership_tool.getAuthenticatedMember()
            member_id = member.getMemberId()
            member_email = self.getMemberEmail(member_id)

            if role_based:
                # Check here if the member is computed based on his local roles
                recipient_mails = []
                role_recipients_rules = subscription.getRecipientsRules(
                    recipients_rule_type='Role Recipient Rule')
                for recipients_rule in role_recipients_rules:
                    current_recipients = recipients_rule.getRecipients(
                                                          object=context)
                    # Cause we may have several persons with the same email
                    has_role = 0
                    for role in recipients_rule.getRoles():
                        if member.has_role(role, context):
                            has_role = 1
                        if not has_role:
                            return 0

                    # Let's check the emails now
                    for mail in current_recipients.keys():
                        if mail not in recipient_mails:
                            recipient_mails.append(mail)

                return member_email in recipient_mails


        explicits = getattr(subscription,
                            self.getExplicitRecipientsRuleId(),
                            None)
        if not explicits:
            return 0

        if not email and not isAno:
            # members
            # FIXME TODO Groups
            return member_id in explicits.getMembers()
        else:
            # Anonymous
            return email in explicits.getEmails()
        return

InitializeClass(SubscriptionsTool)

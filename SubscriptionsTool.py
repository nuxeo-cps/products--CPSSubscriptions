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

"""Subscriptions Tool

Defines the Subscriptions Tool class
"""

from types import DictType, StringType

from Globals import InitializeClass, DTMLFile
from Acquisition import aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from Products.BTreeFolder2.CMFBTreeFolder import CMFBTreeFolder

from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import UniqueObject, getToolByName

from CPSSubscriptionsPermissions import ViewMySubscriptions
from NotificationMessageBody import addNotificationMessageBody

from zLOG import LOG, DEBUG, INFO

##############################################################

# Global ids
SUBSCRIPTION_CONTAINER_ID = '.cps_subscriptions'
EXPLICIT_RECIPIENTS_RULE_ID = 'explicit__recipients_rule'
MAIL_NOTIFICATION_RULE_ID = 'mail__notification_rule'

##############################################################

class SubscriptionsTool(UniqueObject, CMFBTreeFolder):
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
        {'id': 'render_content_for_portal_types',
         'type': 'lines', 'mode':'w',
         'label' : 'Render the content type responsible of the notification \
         within the notification email body for the following content types'},
        {'id': 'render_content_for_events',
         'type': 'lines', 'mode':'w',
         'label' : 'Render the content type responsible of the notification \
         within the notification email bodyfor the following events'},
        {'id': 'notification_scheduling_table',
         'type': 'text', 'mode':'r',
         'label': 'Notification scheduling table'},
        {'id': 'mapping_modes',
         'type': 'string', 'mode':'r',
         'label': 'Subscription modes'},
        )

    mapping_modes = {'weekly' : 'mode_weekly',
                     'monthly': 'mode_monthly',
                     'daily'  : 'mode_daily'}

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
        ) + CMFBTreeFolder.manage_options[0:1] + \
        CMFBTreeFolder.manage_options[2:4]

    security.declareProtected(ManagePortal, 'manage_events')
    manage_events = DTMLFile('zmi/configureEvents', globals())

    security.declareProtected(ManagePortal, 'about')
    about = DTMLFile('zmi/about_portal_subscriptions', globals())

    security.declareProtected(ManagePortal, 'manage_edit_events')
    manage_edit_events = DTMLFile('zmi/editEvents', globals())

    security.declareProtected(ManagePortal, 'manage_edit_event')
    manage_edit_event = DTMLFile('zmi/configureEvent', globals())

    def manage_resetEventMessages(self, REQUEST=None):
        """Reset the email messages to their default values.
        """
        self.resetEvents()
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_edit_events')

    def manage_editDefaultEventMessage(self,
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
        """Edit the default event email messages.
        """
        self._p_changed = 1

        # No %(sthg)s in the error message. It's the purpose of that kind of
        # message.
        if '%' in event_error_email_body:
            event_error_email_body = event_error_email_body.replace('%', '')

        # Notifications
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
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_edit_events')

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
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_edit_events')


    def manage_addEventType(self, event_where, event_id, event_label, REQUEST=None):
        """ Adds a new event id in a given context
        """
        self._p_changed = 1

        if self.mapping_context_events.has_key(event_where):
            if not self.mapping_context_events[event_where].has_key(event_id):
                self.mapping_context_events[event_where][event_id] = event_label
        else:
            self.mapping_context_events[event_where] = {}
            self.mapping_context_events[event_where][event_id] = event_label

        if not self.mapping_event_email_content.has_key(event_id):
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
                self.getUnSubscribeEmailBody(),
                ]

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_events')


    ###################################################
    # SUBSCRIPTIONS TOOL API
    ###################################################

    def __init__(self):
        """Initialization of default properties.

        Core attributs and default messages contents
        """

        # Btree constructor to store notification message body
        CMFBTreeFolder.__init__(self, self.id)

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

        # Rendering content at notification time
        self.render_content_for_portal_types = []
        self.render_content_for_events = []

        # Here, it's stored the notification scheduling table
        # Structure :
        # mode | email | message_ids
        #
        # Mode  : One of the above subscription modes
        # Email : email of the recipient
        # message_ids : list of the message ids stored in the portal_subscriptions
        self.notification_scheduling_table = {}

        self.mapping_modes = {'weekly' : 'mode_weekly',
                              'monthly': 'mode_monthly',
                              'daily'  : 'mode_daily'}

    ######################################################
    #####################################################

    security.declareProtected(ManagePortal, 'addRenderedPortalTypes')
    def addRenderedPortalType(self, portal_type=''):
        """Add a portal type for wich the render of the content
        type will be included into the notification email body.
        """

        self._p_changed = 1

        if (isinstance(portal_type, StringType) and
            portal_type not in self.render_content_for_portal_types):
            self.render_content_for_portal_types.append(portal_type)
            return 1
        return 0

    security.declareProtected(ManagePortal, 'addRenderedEvents')
    def addRenderedEvent(self, event_id=''):
        """Add an event for wich the render of the content
        type will be included into the notification email body.
        """

        self._p_changed = 1

        if (isinstance(event_id, StringType) and
            event_id not in self.render_content_for_events):
            self.render_content_for_events.append(event_id)
            return 1
        return 0

    security.declarePublic('getRenderedPortalTypes')
    def getRenderedPortalTypes(self):
        """Return the portal_types that we are gonna render
        and add the rendering within the email notification body
        """
        return self.render_content_for_portal_types

    security.declarePublic('getRenderedEvents')
    def getRenderedEvents(self):
        """Return the events for wich  we are gonna render the content
        type which is responsible of the notifications
        and then add this rendering within the email notification body
        """
        return self.render_content_for_events

    ###########################################################
    ###########################################################

    security.declareProtected(ManagePortal, 'setupEvents')
    def setupEvents(self):
        """ Setup events on which to react
        """
        portal = getToolByName(self, 'portal_url').getPortalObject()
        mapping_context_events = portal.getEvents()
        for context in mapping_context_events.keys():
            for event_id in mapping_context_events[context].keys():
                self.manage_addEventType(context,
                                         event_id,
                                         mapping_context_events[context]
                                         [event_id])

    security.declarePublic('resetEvents')
    def resetEvents(self):
        """ Reset events
        """
        self.__init__()
        self.setupEvents()

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

    security.declarePublic('getSubscribablePortalTypes')
    def getSubscribablePortalTypes(self):
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

    security.declarePublic('getI18nFor')
    def getI18nFor(self, event_id=''):
        """Return the i18n string for the given event_id
        """
        for key_portal_type in self.mapping_context_events.keys():
            for key_event in self.mapping_context_events[key_portal_type].keys():
                if key_event == event_id:
                    return self.mapping_context_events[key_portal_type][key_event]

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

        if object is None:
            return subscriptions

        subscriptionContainer = getattr(object,
                                        self.getSubscriptionContainerId(),
                                        None)

        if subscriptionContainer:
            subscriptions += subscriptionContainer.getSubscriptions()
            if event_type:
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
            container = infos['context']
            object = container
        else:
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
                    if isinstance(pt_recipients, DictType):
                        for pt_recipient in pt_recipients.keys():
                            recipients[pt_recipient] = pt_recipients[pt_recipient]
                    else:
                        LOG("::CPSSubscriptions :: ComputeRecipientsRules ERROR",
                            INFO,
                            "You should provide a dictionnary",
                            pt_recipient_rule.absolute_url())
        return recipients

    #############################################################
    #############################################################

    def _makeEltDict(self, ob, subscription):
        """Build a dict with an object

        Used within the getAllSubscriptionsFor method
        """
        elt = {}
        elt['title'] = ob.title_or_id()
        if getattr(ob, 'getContent'):
            doc = ob.getContent()
            elt['description'] = doc.Description()
        else:
            elt['description'] = ob.Description()
        elt['path'] = ob.absolute_url()
        event_id = subscription.id.split('__')[1]
        elt['event_id'] = event_id
        return elt

    security.declareProtected(ViewMySubscriptions, 'getAllSubscriptionsFor')
    def getAllSubscriptionsFor(self, member_id='', context=None):
        """Returns all the subscriptions for a given member/email or
        for the authenticated member.

        It's possible to restrict to the context as well.

        Catalog research. getRecipients is indexed for the subscriptions
        container.

        Anonymous can't acces this ressource since it's protected by
        the ViewMySubscriptions permission reserved to members.
        """

        #
        # Preparing needed information for the research
        # Authenticated member or member given member_id ?
        # Localy or globaly ?
        #

        # Member information
        if not member_id:
            membership_tool = getToolByName(self, 'portal_membership')
            member_id = membership_tool.getAuthenticatedMember().getMemberId()
        email = self.getMemberEmail(member_id)

        # Place
        if context is not None:
            path = context.absolute_url()
        else:
            path = getToolByName(self, 'portal_url').getPortalPath()

        # Get the subscriptions containers
        catalog = getToolByName(self, 'portal_catalog')
        portal_type = 'CPS PlaceFull Subscription Container'

        containers = catalog.searchResults({'portal_type':
                                            portal_type,
                                            'path':path,})
        LOG(":: CPSSubscriptions :: catalog search for containers",
            INFO,
            str(containers))

        #
        # Now let's get the subcription containers and check if the computed
        # member is a subscriber from there.
        #

        subscriptions_list = []
        for container in containers:
            container_parent = aq_parent(aq_inner(container.getObject()))
            # Fetch the subscriptions in the given container
            subscriptions = self.getSubscriptionsFor(None, container_parent)
            for subscription in subscriptions:
                for recipients_rule in subscription.getRecipientsRules():

                    #
                    # Explict subscriptions specific case
                    #
                    # The reason is that the member might have subscribe
                    # from another place thant the place where the container is
                    # For instance :
                    #     /sections (place where the subscriptions container)
                    #     /sections/sub1 (Place where the member subscribed)
                    #     /sections/sub2 (nothing)
                    #     /Sections/sub2/subsub2 (Another place where the
                    #                             member subscribed)
                    #

                    if recipients_rule.meta_type == 'Explicit Recipients Rule':
                        subscriber = recipients_rule.getMemberStructById(member_id)
                        if subscriber != -1:
                            urls = subscriber['subscription_relative_url']
                            for url in urls:
                                ob = self.restrictedTraverse(url)
                                elt = self._makeEltDict(ob, subscription)
                                subscriptions_list.append(elt)

                    #
                    # Standard case (Role based computed recipients)
                    #

                    else:
                        recipients = recipients_rule.getRecipients('', container_parent, {})
                        if email in recipients.keys():
                            elt = self._makeEltDict(container_parent, subscription)
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
            return member_id in explicits.getMemberIds(context=context)
        else:
            # Anonymous
            return email in explicits.getEmails()
        return

    ################################################################
    ################################################################

    security.declareProtected(ManagePortal, 'addNotificationMessageBodyObject')
    def addNotificationMessageBodyObject(self, message_body='', mime_type='text/plain'):
        """Add a notification Message Body
        """
        id = addNotificationMessageBody(self,
                                        message_body=message_body,
                                        mime_type=mime_type)
        return id

    security.declarePublic('getSubscriptionModes')
    def getSubscriptionModes(self):
        """Returns the susbcriptions mode
        """
        return self.mapping_modes.values()

    def scheduleNotificationMessageFor(self, user_mode, email, message_id):
        """Add within the scheduling table the message_id for a the given user within
        the given category
        """

        self._p_changed = 1

        if user_mode and email and message_id:
            if not self.notification_scheduling_table.has_key(user_mode):
                if user_mode in self.getSubscriptionModes():
                    self.notification_scheduling_table[user_mode] = {}
                else:
                    return -1

            mode_entry = self.notification_scheduling_table[user_mode]
            if not mode_entry.has_key(email):
                mode_entry[email] = []

            if message_id not in mode_entry[email]:
                mode_entry[email].append(message_id)

            self.notification_scheduling_table[user_mode] = mode_entry
            return 0
        return -1

    def _getMailInfoFor(self, subscription_mode, email_to, messages):
        """Build the infos dict

        It will compile several notification messages body.
        """

        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_title = getattr(portal, 'title', 'Portal')
        mcat = self.Localizer.default

        infos = {}
        infos['sender_email'] = getattr(portal,
                                        'email_from_address',
                                        'nobody@nobody.com')
        infos['sender_name']  = getattr(portal,
                                        'email_from_name',
                                        'Portal administrator')
        infos['to'] = email_to

        # Message body
        compiled_body_text = ""
        compiled_body_html = ""
        for message_id in messages:
            message = getattr(self, message_id, None)
            if message is not None:
                mime_type = message.getMimeType()
                if mime_type == 'text/html':
                    compiled_body_html += "<br /><br />"
                    compiled_body_html += message.getMessageBody()
                else:
                    compiled_body_text += '\n\n'
                    compiled_body_text += message.getMessageBody()

        if compiled_body_html:
            infos_html = infos
            infos_html['body'] = (compiled_body_html, 'text/html')
            subscription_mode_label = mcat('mode_'+subscription_mode) + ' V2 '
            infos_html['subject'] = '[%s] %s' %(portal_title, subscription_mode_label)
        else:
            infos_html = None

        if compiled_body_text:
            subscription_mode_label = mcat('mode_'+subscription_mode) + ' V1 '
            infos['subject'] = '[%s] %s' %(portal_title, subscription_mode_label)
            infos['body'] = (compiled_body_text, 'text/plain')
        else:
            infos = None

        return infos, infos_html

    security.declareProtected(ManagePortal, 'scheduleMessages')
    def scheduleMessages(self, subscription_mode=''):
        """Schedule Message for a given subscription_mode
        """

        from Notifications import NotificationRule
        notification_vector = NotificationRule('fake')

        if subscription_mode in self.mapping_modes.keys():
            table = self.notification_scheduling_table.get(
                self.mapping_modes[subscription_mode], [])

            # XXX send them all at the same time with bcc
            for email in table.keys():
                text, html = self._getMailInfoFor(subscription_mode,
                                                  email,
                                                  table[email])
                portal = getToolByName(self, 'portal_url').getPortalObject()
                mailhost = portal.MailHost
                # XXX
                # For the moment I have to send 2 sepate mail since
                # the NotificationRule can't handle 2 body parts
                if text is not None:
                    notification_vector.sendMail(mail_infos=text, mailhost=mailhost)
                if html is not None:
                    notification_vector.sendMail(mail_infos=html, mailhost=mailhost)

            # Cleaning the scheduling table
            for email in table.keys():
                table[email] = []
            self.notification_scheduling_table[
                self.mapping_modes[subscription_mode]] = table
        else:
            return -1

InitializeClass(SubscriptionsTool)

# Copyright (c) 2004-2008 Nuxeo SAS <http://nuxeo.com>
# Copyright (c) 2004 CGEY <http://cgey.com>
# Copyright (c) 2004 Ministere de L'interieur (MISILL)
#               <http://www.interieur.gouv.fr/>
# Authors:
# Julien Anguenot <ja@nuxeo.com>
# Florent Guillaume <fg@nuxeo.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# $Id$

__author__ = "Julien Anguenot <mailto:ja@nuxeo.com>"

"""Subscriptions Tool

Defines the Subscriptions Tool class
"""

from logging import getLogger
import warnings

from types import DictType, StringType

from Globals import InitializeClass, DTMLFile
from Acquisition import aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.ActionProviderBase import ActionProviderBase

from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent

from permissions import ViewMySubscriptions
from permissions import CanSubscribe
from permissions import ManageSubscriptions

from Notifications import MailNotificationRule
from NotificationMessageBody import addNotificationMessageBody
from EventSubscriptionsManager import get_event_subscriptions_manager

from Products.CPSSubscriptions.interfaces import ISubscriptionsTool

##############################################################

# Global ids
SUBSCRIPTION_CONTAINER_ID = '.cps_subscriptions'
EXPLICIT_RECIPIENTS_RULE_ID = 'explicit__recipients_rule'
MAIL_NOTIFICATION_RULE_ID = 'mail__notification_rule'
SUBSCRIPTION_PREFIX = 'subscription__'

##############################################################

logger = getLogger('CPSSubscriptions.SubscriptionsTool')

class SubscriptionsTool(UniqueObject, CMFBTreeFolder, ActionProviderBase):
    """Subscriptions Tool

    portal_subcriptions is the central tool with the necessary methods
    to query the subscriptions and execute them.

    The subscriptions are looked up locally in a .cps_subscriptions folder in
    the object.
    """

    __implements__ = ActionProviderBase.__implements__

    implements(ISubscriptionsTool)

    id = 'portal_subscriptions'
    meta_type = 'Subscriptions Tool'
    _actions = ()

    security = ClassSecurityInfo()

    _properties = (
        {'id': 'notify_hidden_object',
         'type': 'boolean', 'mode':'w',
         'label' : 'Notify hidden files'}, # FIXME Unused for now
        {'id': 'user_is_sender',
         'type': 'boolean', 'mode':'w',
         'label' : "Use user's email address as mail from"},
        {'id': 'max_recipients_per_notification',
         'type': 'int', 'mode':'w',
         'label': 'Max recipients per notification message'},
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
        {'id': 'mapping_local_roles_context',
         'type': 'string', 'mode':'r',
         'label': 'Local roles within the different context'},
        {'id': 'ignore_events', 'type': 'boolean', 'mode': 'w',
         'label': "Ignore events"},
        )

    # Maximim recipients (emails) for one notification.
    # Check the maik server capability
    max_recipients_per_notification = 20

    mapping_modes = {'weekly' : 'mode_weekly',
                     'monthly': 'mode_monthly',
                     'daily'  : 'mode_daily'}

    mapping_local_roles_context = {}
    ignore_events = False
    user_is_sender = False

    ###################################################
    # ZMI
    ###################################################

    manage_options = (
        {'label': "About",
         'action': 'about'
         },
        ) + ActionProviderBase.manage_options + (
        {'label': "Events / contexts",
         'action': 'manage_events',
         },
        {'label': "Local roles / contexts",
         'action': 'manage_local_roles_in_contexts',
         },
        {'label': "Events / Notification messages",
         'action': 'manage_edit_events',
         },
        ) + CMFBTreeFolder.manage_options[0:1] + (
        {'label': 'Export',
         'action': 'manage_genericSetupExport.html', },
        ) + CMFBTreeFolder.manage_options[2:4]

    security.declareProtected(ManagePortal, 'manage_events')
    manage_events = DTMLFile('zmi/configureEvents', globals())

    security.declareProtected(ManagePortal, 'about')
    about = DTMLFile('zmi/about_portal_subscriptions', globals())

    security.declareProtected(ManagePortal, 'manage_edit_events')
    manage_edit_events = DTMLFile('zmi/editEvents', globals())

    security.declareProtected(ManagePortal, 'manage_edit_event')
    manage_edit_event = DTMLFile('zmi/configureEvent', globals())

    security.declareProtected(ManagePortal, 'manage_local_roles_in_contexts')
    manage_local_roles_in_contexts = DTMLFile(
        'zmi/configureLocalRoles', globals())

    def manage_resetEventMessages(self, REQUEST=None):
        """Reset the email messages to their default values.
        """
        warnings.warn("manage_resetEventMessages is obsolete and will be "
                      "removed in CPS 3.5.0", DeprecationWarning, 2)
        self.resetEvents()
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(
                self.absolute_url() + '/manage_edit_events')

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
                                       event_default_email_title=None,
                                       event_default_email_body=None,
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

        # Defaults
        if event_default_email_title is not None:
            self.event_default_email_title = event_default_email_title
        if event_default_email_body is not None:
            self.event_default_email_body = event_default_email_body

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
            REQUEST.RESPONSE.redirect(
                self.absolute_url() + '/manage_edit_events')

    def manage_editEventMessage(self,
                                event_id,
                                event_email_title,
                                event_email_body,
                                REQUEST=None):
        """Edit a custom event message
        """
        self._p_changed = 1

        struct = [event_email_title,
                  event_email_body,
                  ]

        self.mapping_event_email_content[event_id] = struct

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(
                self.absolute_url() + '/manage_edit_events')


    def manage_addEventType(self, event_where, event_id, event_label,
                            REQUEST=None):
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
                ]

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_events')

    #######################################################################

    def manage_addLocalRoleArea(self,
                                area_portal_type='',
                                REQUEST=None):
        """Add a local role area
        """

        if area_portal_type:
            self.setLocalRolesArea(area=area_portal_type)

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() +
                                      '/manage_local_roles_in_contexts')

    def manage_addPortalTypeToArea(self,
                                   area_portal_type='',
                                   portal_type='',
                                   REQUEST=None):
        """Add a new portal_type within an area
        """

        if area_portal_type and area_portal_type in self.getLocalRoleAreas():
            if portal_type:
                self.addPortalTypeToArea(area_portal_type, portal_type)

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() +
                                      '/manage_local_roles_in_contexts')

    def manage_addLocalRoleToPortalTypeToArea(self,
                                              area_portal_type='',
                                              portal_type='',
                                              role_id='',
                                              role_label='',
                                              REQUEST=None):
        """Add a new local role within a portal_type within an area
        """

        if area_portal_type and area_portal_type in self.getLocalRoleAreas():
            if portal_type and portal_type in self.getLocalRoleArea(
                area_portal_type).keys():
                self.addLocalRoleToPortalTypeToArea(area_portal_type,
                                                    portal_type,
                                                    role_id,
                                                    role_label)

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() +
                                      '/manage_local_roles_in_contexts')

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
        self.render_content_for_portal_types = ()
        self.render_content_for_events = ()

        # Here, it's stored the notification scheduling table
        # Structure :
        # mode | email | message_ids
        #
        # Mode  : One of the above subscription modes
        # Email : email of the recipient
        # message_ids : list of the message ids stored in the
        # portal_subscriptions

        self.notification_scheduling_table = {}

        self.mapping_modes = {'weekly' : 'mode_weekly',
                              'monthly': 'mode_monthly',
                              'daily'  : 'mode_daily'}

        # Local roles / context
        self.mapping_local_roles_context = {}

    #####################################################

    security.declareProtected(ManagePortal, 'addRenderedPortalType')
    def addRenderedPortalType(self, portal_type=''):
        """Add a portal type for wich the render of the content
        type will be included into the notification email body.
        """
        if (isinstance(portal_type, StringType) and
            portal_type not in self.render_content_for_portal_types):
            self.render_content_for_portal_types += (portal_type,)
            return 1
        return 0

    security.declareProtected(ManagePortal, 'addRenderedEvent')
    def addRenderedEvent(self, event_id=''):
        """Add an event for wich the render of the content
        type will be included into the notification email body.
        """
        if (isinstance(event_id, StringType) and
            event_id not in self.render_content_for_events):
            self.render_content_for_events += (event_id,)
            return 1
        return 0

    security.declarePublic('getRenderedPortalTypes')
    def getRenderedPortalTypes(self):
        """Return the portal_types that we are going to render
        and add the rendering within the email notification body
        """
        return self.render_content_for_portal_types

    security.declarePublic('getRenderedEvents')
    def getRenderedEvents(self):
        """Return the events for wich we are going to render the content
        type which is responsible of the notifications
        and then add this rendering within the email notification body
        """
        return self.render_content_for_events

    ###########################################################

    security.declareProtected(ManagePortal, 'setupEvents')
    def setupEvents(self):
        """Setup events on which to react.
        """

        warnings.warn("setupEvents is obsolete and will be "
                      "removed in CPS 3.5.0", DeprecationWarning, 2)

        portal = getToolByName(self, 'portal_url').getPortalObject()
        # FIXME AT: getEvents should not be a skin script...
        mapping_context_events = portal.getEvents()
        for context in mapping_context_events.keys():
            for event_id in mapping_context_events[context].keys():
                self.manage_addEventType(context,
                                         event_id,
                                         mapping_context_events[context]
                                         [event_id])

    security.declarePublic('resetEvents')
    def resetEvents(self):
        """Reset events.
        """
        warnings.warn("resetEvents is obsolete and will be "
                      "removed in CPS 3.5.0", DeprecationWarning, 2)
        self.__init__()
        self.setupEvents()

    security.declarePublic('getSubscriptionContainerId')
    def getSubscriptionContainerId(self):
        """Returns the default id for subscription containers.

        .cps_subscriptions by default
        """
        return SUBSCRIPTION_CONTAINER_ID

    security.declarePublic('getExplicitRecipientsRuleId')
    def getExplicitRecipientsRuleId(self):
        """Returns an in use id.

        Id in use for the ExplicitRecipientsRule object
        """
        return EXPLICIT_RECIPIENTS_RULE_ID

    security.declarePublic('getMailNotificationRuleObjectId')
    def getMailNotificationRuleObjectId(self):
        """ Returns an in use id.

        Id in use for the MailNoticationRule object.
        """
        return MAIL_NOTIFICATION_RULE_ID

    security.declarePublic('getSubscriptionObjectPrefix')
    def getSubscriptionObjectPrefix(self):
        """Return the default prefix used for subscription

        <subscription__>event_id
        """
        return SUBSCRIPTION_PREFIX

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
                # if the event message is not found, use the default message
                return self.event_default_email_title
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
                # if the event message is not found, use the default message
                return self.event_default_email_body
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
            context_portal_type = getattr(context, 'portal_type', '')
            if self.mapping_context_events.has_key(context_portal_type):
                return self.mapping_context_events[context_portal_type]
        return {}

    security.declarePublic('getFilteredAllowedToSubscribeEventsFromContext')
    def getFilteredAllowedToSubscribeEventsFromContext(self, context=None):
        """Returns events given context filtered on roles
        """
        mtool = getToolByName(self, 'portal_membership')
        auth_member = mtool.getAuthenticatedMember()
        auth_roles = auth_member.getRolesInContext(context)

        event_ids_from_context = self.getEventsFromContext(context).keys()
        container = self.getSubscriptionContainerFromContext(context)

        res = {}
        for event_id in event_ids_from_context:
            subscription = container.getSubscriptionById(event_id)
            if subscription is not None:
                roles_allowed = subscription.getRolesAllowedToSubscribe()
            else:
                roles_allowed = []

            ok = 0
            # No filter in here
            if roles_allowed == []:
                ok = 1
            for role_allowed in roles_allowed:
                if role_allowed in auth_roles:
                    ok = 1
            if ok:
                res[event_id] = self.getI18nFor(event_id)
        return res

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
            for key_event in self.mapping_context_events[
                key_portal_type].keys():
                if key_event == event_id:
                    return self.mapping_context_events[
                        key_portal_type][key_event]

    #########################################################

    security.declarePublic('addSusbcriptionContainerFromContext')
    def addSubscriptionContainerInContext(self, context):
        """Add a subscription container in the context
        """
        if context is None:
            return None

        subscription_id = self.getSubscriptionContainerId()
        if context.isPrincipiaFolderish:
            if subscription_id not in context.objectIds():
                context.manage_addProduct[
                    'CPSSubscriptions'].addSubscriptionContainer()
        else:
            # `context` is not a folderish document so we can't create
            # a subscription container within.
            return self.getSubscriptionContainerFromContext(
                aq_parent(aq_inner(context)), force_local_creation=True)

        return getattr(context, subscription_id)

    security.declarePublic('getSusbcriptionContainerFromContext')
    def getSubscriptionContainerFromContext(self, context,
                                            force_local_creation=0):
        """Returns a SubscriptionContainer relative to the context.

        Lookup to find one through acquisition with the accurate
        rights for the user to manage it. Note the user is supposed to
        have the rights to manage the container in the context if not
        then this method will return None.
        """
        # Lookup container by acquisition
        container = getattr(context, self.getSubscriptionContainerId(), None)

        # No subscription container by acquisition
        # create one in the context if the current member
        # has the ModifyPortalContent permission
        if ((container is None or force_local_creation)
            and _checkPermission(ModifyPortalContent, context)):
            container = self.addSubscriptionContainerInContext(context)

        # If the container is looked up by acquisition but the current
        # user doesn't have the right permissions to perform
        # modifications on it then create on in the context
        if not _checkPermission(ManageSubscriptions, container):
            container = self.addSubscriptionContainerInContext(context)

        return container

    security.declarePrivate('notify_processed_event')
    def notify_processed_event(self, event_type, object, infos):
        """EventManager's callable.
        """
        subscriptions = self.getSubscriptionsFor(event_type, object, infos)
        for subscription in subscriptions:
            if subscription.isInterestedInEvent(event_type, object, infos):
                subscription.sendEvent(event_type, object, infos)

    security.declarePrivate("notify_event")
    def notify_event(self, event_type, object, infos):
        """Standard event hook.

        Get the applicable subscriptions. Sends the event to the
        subscriptions.

        For workflow events, infos must contain the additional
        keyword arguments passed to the transition.
        """
        if self.ignore_events:
            return

        # Pre-filtering : we don't want to notify the user on
        # repository objects
        if not 'portal_repository' in object.getPhysicalPath():
            get_event_subscriptions_manager().push(event_type, object, infos)

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
                            recipients[pt_recipient] = pt_recipients[
                                pt_recipient]
                    else:
                        logger.debug("ComputeRecipientsRules ERROR: "
                                     "You should provide a dictionnary %s"
                                     % pt_recipient_rule.absolute_url())
        return recipients

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

        # still canSubscribe ?
        sub = getattr(ob, '.cps_subscriptions', 0)
        if sub:
            elt['canSubscribe'] = _checkPermission(CanSubscribe, sub)
        else:
            elt['canSubscribe'] = 0

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
        membership_tool = getToolByName(self, 'portal_membership')
        if not member_id:
            member_id = membership_tool.getAuthenticatedMember().getMemberId()
        email = membership_tool.getEmailFromUsername(member_id)

        # Place
        if context is not None:
            path = context.absolute_url()
        else:
            path = getToolByName(self, 'portal_url').getPortalPath()

        # Get the subscriptions containers
        catalog = getToolByName(self, 'portal_catalog')
        portal_type = 'CPS PlaceFull Subscription Container'
        query = {'portal_type': portal_type, 'path': path}

        # Here we search the Catalog without view restriction because
        # .cps_subsciption may be herited from unaccessible parent
        # folder
        containers = catalog.unrestrictedSearchResults(None, **query)
        logger.debug("catalog search for containers %s %s"
                     % (query, [x.getPath() for x in containers]))

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
                        subscriber = recipients_rule.getMemberStructById(
                            member_id)
                        if subscriber != -1:
                            urls = subscriber['subscription_relative_url']
                            for url in urls:
                                ob = self.restrictedTraverse(url, None)
                                if ob is None:
                                    # ob has since been removed
                                    continue
                                elt = self._makeEltDict(ob, subscription)
                                subscriptions_list.append(elt)

                    #
                    # Standard case (Role based computed recipients)
                    #

                    else:
                        recipients = recipients_rule.getRecipients(
                            '', container_parent, {})
                        if email in recipients.keys():
                            elt = self._makeEltDict(container_parent,
                                                    subscription)
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
            member_email = membership_tool.getEmailFromUsername(member_id)

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

    security.declareProtected(ManagePortal, 'addNotificationMessageBodyObject')
    def addNotificationMessageBodyObject(self, message_body='',
                                         mime_type='text/plain'):
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
        """Add within the scheduling table the message_id for a the given user
        within the given category
        """
        logger.debug("scheduleNotificationMessageFor user_mode = %s" % user_mode)
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

    security.declarePublic('getMailSenderInfo')
    def getMailSenderInfo(self, use_portal_title=0):
        """Return the sender information (name and email address)

        If use_portal_title is set to 1, then the portal title is used instead
        of the portal administrator name.
        """
        if self.user_is_sender:
            member = getToolByName(self,
                                   'portal_membership').getAuthenticatedMember()
            address = member.getProperty('email', None)
            name = member.getProperty('fullname', None)
            if address is not None and name is not None:
                return address, name

        # otherwise default to global info
        portal = getToolByName(self, 'portal_url').getPortalObject()
        sender_email = portal.getProperty('email_from_address',
                                          'nobody@nobody.com')
        if use_portal_title == 1:
            sender_name = portal.title_or_id()
        else:
            sender_name = portal.getProperty('email_from_name',
                                              'Portal administrator')
        return sender_email, sender_name

    def _getMailInfoFor(self, subscription_mode, email_to, messages):
        """Build the infos dict

        It will compile several notification messages body.
        """

        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_title = getattr(portal, 'title', 'Portal')
        mcat = self.translation_service

        infos = {}
        sender_email, sender_name = self.getMailSenderInfo()
        infos['sender_email'] = sender_email
        infos['sender_name']  = sender_name
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
            subscription_mode_label = mcat('mode_'+subscription_mode).encode(
                "ISO-8859-15", "ignore") + ' V2 '
            infos_html['subject'] = '[%s] %s' %(
                portal_title, subscription_mode_label)
        else:
            infos_html = None

        if compiled_body_text:
            subscription_mode_label = mcat('mode_'+subscription_mode).encode(
                "ISO-8859-15", "ignore") + ' V1 '
            infos['subject'] = '[%s] %s' %(portal_title,
                                           subscription_mode_label)
            infos['body'] = (compiled_body_text, 'text/plain')
        else:
            infos = None

        return infos, infos_html

    security.declareProtected(ManagePortal, 'scheduleMessages')
    def scheduleMessages(self, subscription_mode=''):
        """Schedule Message for a given subscription_mode
        """

        self._p_changed = 1

        notification_vector = MailNotificationRule('fake')

        if subscription_mode in self.mapping_modes.keys():
            table = self.notification_scheduling_table.get(
                self.mapping_modes[subscription_mode], {})

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
                    notification_vector.sendMail(mail_infos=text,
                                                 mailhost=mailhost)
                if html is not None:
                    notification_vector.sendMail(mail_infos=html,
                                                 mailhost=mailhost)

            # Cleaning the scheduling table
            for email in table.keys():
                table[email] = []
            self.notification_scheduling_table[
                self.mapping_modes[subscription_mode]] = table
            return "Notifications sent"
        else:
            return -1

    ###############################################################

    security.declareProtected(ManagePortal, 'setLocalRolesArea')
    def setLocalRolesArea(self, area='', value={}):
        """Add a portal area

        An area is the 'Workspace' area or the 'Section' area or whatever
        sub-part of your cps portal you may define it corresponds to the
        portal_type of the main container

        value : dictionnary containing the portal_type within the area
        and then the corresponding local roles with the i18n labels

        cf. cps_subscriptions_installer/getCPSSubscriptionsRelevantLocalRoles
        """
        self._p_changed = 1

        if area and area not in self.getLocalRoleAreas():
            self.mapping_local_roles_context[area] =  value
        else:
            for portal_type in value.keys():
                if (portal_type not in
                    self.mapping_local_roles_context[area].keys()):
                    self.mapping_local_roles_context[
                        area][portal_type] = value[portal_type]
                else:
                    for role in value[portal_type].keys():
                        self.mapping_local_roles_context[area][
                            portal_type][role] = value[portal_type][role]

    security.declarePublic('getLocalRoleAreas')
    def getLocalRoleAreas(self):
        """Return the different local role areas defined
        """
        return self.mapping_local_roles_context.keys()

    security.declarePublic('getLocalRoleArea')
    def getLocalRoleArea(self, area=''):
        """Return a local are given an area id

        It returns a dictionnary struct.
        cf. cps_subscriptions_installer/getCPSSubscriptionsRelevantLocalRoles
        """
        if not area:
            self.setLocalRolesArea(area=area)
        return self.mapping_local_roles_context.get(area)

    security.declareProtected(ManagePortal, 'addPortalTypeToArea')
    def addPortalTypeToArea(self, area='', portal_type=''):
        """Add a portal_type to an area
        """
        self._p_changed = 1

        if area and area in self.getLocalRoleAreas():
            if (portal_type and
                portal_type not in
                self.mapping_local_roles_context[area].keys()):
                self.mapping_local_roles_context[area][portal_type] = {}

    security.declareProtected(ManagePortal, 'addLocalRoleToPortalTypeToArea')
    def addLocalRoleToPortalTypeToArea(self,
                                       area='',
                                       portal_type='',
                                       role_id='',
                                       role_label=''):
        """Add a new local role to a given portal_type within a given area
        """
        self._p_changed = 1

        if area and area in self.getLocalRoleAreas():
            if portal_type and portal_type in self.getLocalRoleArea(
                area).keys():
                if role_id and role_id not in self.getLocalRoleArea(area)[
                    portal_type]:
                    if not role_label:
                        role_label = role_id
                    self.mapping_local_roles_context[area][portal_type][
                        role_id] = role_label

    ##############################################################

    def _getLocalRoleAreaFromContext(self, context):
        """Get Local Role area from context
        """
        content_path = self.portal_url.getRelativeContentPath(context)
        for container_id in content_path:
            ob = self.restrictedTraverse(container_id)
            portal_type = getattr(ob, 'portal_type', None)
            if (portal_type is not None and
                portal_type in self.getLocalRoleAreas()):
                return portal_type
        return None

    security.declareProtected(ManagePortal, 'setLocalRolesToContext')
    def setLocalRolesToContext(self, area=None, context=None,
                               local_roles_mapping={}):
        """Add local roles to a given context (portal_type)

        cf. cps_subscriptions_installer/getCPSSubscriptionsRelevantLocalRoles
        """
        self._p_changed = 1
        self.mapping_local_roles_context[area][context] = local_roles_mapping

    security.declareProtected(View, 'getRelevantLocalRolesFromContext')
    def getRelevantLocalRolesFromContext(self, context=None):
        """Returns relevant local roles for a given context (portal_type)

        Only used to display relevant local roles to the user
        """
        if context is not None:
            context_area = self._getLocalRoleAreaFromContext(context)
            context_portal_type = getattr(context, 'portal_type', None)
            if (context_area is not None and
                context_portal_type is not None and
                context_portal_type in self.getContainerPortalTypes()):
                area = self.getLocalRoleArea(context_area)
                return area.get(context_portal_type, {})
        return {}

    #########################################################################

    def sendmail(self, infos={}):
        """Send a mail given a mapping
        """

        # Add acquisition so that it can found the mailhost object at
        # the root of CPS.
        notification_obj = MailNotificationRule('notification').__of__(self)

        cerror = notification_obj.sendMail(infos)
        return cerror

    def all_meta_types(self):
        """Allowed meta types
        """
        return ()

InitializeClass(SubscriptionsTool)

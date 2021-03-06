# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2004 CGEY <http://cgey.com>
# Copyright (c) 2004 Ministere de L'intérieur (MISILL)
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

""" Subscription Class
"""
import logging
from Globals import InitializeClass, MessageDialog
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from Products.CMFCore.PortalFolder import PortalFolder

logger = logging.getLogger('Products.CPSSubscriptions.Subscription')

class Subscription(PortalFolder):
    """ Subscription

    Placefull Object containing subscription information.
    """

    meta_type = 'CPS Subscription Configuration'
    portal_type = meta_type

    security = ClassSecurityInfo()

    _properties = PortalFolder._properties + \
                  ({'id': 'filter_event_types',
                    'type': 'lines',
                    'mode': 'w',
                    'label': 'Filter Event Types'},
                   {'id': 'filter_object_types',
                    'type': 'lines',
                    'mode': 'w',
                    'label': 'Filter Object Types'},
                   {'id': 'recipient_emails_black_list',
                    'type': 'lines',
                    'mode': 'w',
                    'label': 'Recipient Emails Black List'},
                   {'id': 'roles_allowed_to_subscribe',
                    'type':'lines',
                    'mode':'w',
                    'label' : 'Roles Allowed to susbcribe'},
                   {'id': 'notification_type',
                    'type': 'string',
                    'mode': 'w',
                    'label': 'Notification Type'},
                   )

    filter_event_types = []
    filter_object_types = []
    roles_allowed_to_subscribe = []
    recipient_emails_black_list = []
    notification_type = 'email'

    def __init__(self, id, title=''):
        """Constructor
        """
        PortalFolder.__init__(self, id, title)

        # The event types on which to react.
        self.filter_event_types = []

        # The types of the objects concerned by the subscription.
        self.filter_object_types = []

        # The recipients emails blocked by the subscription
        self.recipients_emails_black_list = []

        # The type of notifications in use
        self.notification_type = 'email'

    def getFilterEventTypes(self):
        """ Returns the event types on which to react

        ex: workflow_create, workflow_in_publish
        """
        return self.filter_event_types

    def addEventType(self, event_type):
        """ Adds a new event type on wich
        """
        if event_type not in self.getFilterEventTypes():
            self.filter_event_types += [event_type]

    def getFilterObjectTypes(self):
        """Returns the types of objects concerned by the subscription.

        The subscription is valid only if the
        context object's portal_type is in object_types.
        """
        return self.filter_object_types

    def getRolesAllowedToSubscribe(self):
        """Returns the list of roles allowed to susbcribe to this event

        [] means everybody
        """
        return self.roles_allowed_to_subscribe

    def setRolesAllowedToSubscribe(self, roles=()):
        """Set the roles allowed to susbcribe
        """
        self._p_changed = 1
        self.roles_allowed_to_subscribe = roles

    def addRolesAllowedToSSubscribe(self, role=''):
        """Add a role allowed to subscribe to this event
        """
        if role and role not in self.getTRolesAllowedToSubscribe():
            self.roles_allowed_to_subscribe.append(role)

    def addObjectType(self, object_type):
        """Adds a new object type concerned with the subscription.
        """
        if object_type not in self.getFilterObjectTypes():
            self.filter_object_types += [object_type]

    def getRecipientEmailsBlackList(self):
        """ Returns the list of emails blocked by the
        subscription.
        """
        return self.recipient_emails_black_list

    def updateRecipientEmailsBlackList(self, emails=[]):
        """ Adds a new email to the emails black list
        """
        self.recipient_emails_black_list = emails

    def isInterestedInEvent(self, event_type, object, infos):
        """Is the subscription interested in the given event."""
        filtered_event_types = self.getFilterEventTypes()
        if filtered_event_types == [] or not event_type:
            return 1
        else:
            return event_type in filtered_event_types

    def getNotificationRules(self):
        """ Returns the notification rule associate to this object
        """
        return [x for x in self.objectValues() if hasattr(x,
                                                       'notifyRecipients')]
    def sendEvent(self, event_type, object, infos, with_groups=False):
        """Send an event to the subscription.
        """

        #
        # Computing recipients for this subscription
        #

        recipients_rules = self.getRecipientsRules()
        emails = {}
        groups = {}

        for recipient_rule in recipients_rules:
            pt_recipients = recipient_rule.getRecipients(
                event_type, object, infos, expand_groups=not with_groups)
            if with_groups:
                pt_emails, pt_groups = pt_recipients
                groups.update(pt_groups)
            else:
                pt_emails = pt_recipients

            for email, v in pt_emails.items():
                if email not in self.getRecipientEmailsBlackList():
                    emails[email] = v
                else:
                    logger.debug("sendEvent: black list for %r", pt_recipient)

        #
        # Notify the recipients
        # Check all the notification rules for this subscription
        #

        notification_rules = self.getNotificationRules()
        for notification_rule in notification_rules:
            notification_rule.notifyRecipients(event_type,
                                               object,
                                               infos,
                                               emails=emails.keys(),
                                               groups=groups.keys())

    def getRecipientsRules(self, recipients_rule_type=None):
        """Get the recipient rules objects.

        if recipient_rule_type is None, then we return all
        the recipients rule objects defined for a this given
        subscription object. If not None we return the given
       recipients rule objects matching the requested type.

        The different types of recipients rule objects :
          - Role Recipients Rulz
          - Explicit Recipients Rule
          - Computed Recipents Rule
          - Workflow Implied Recipients Rule

        """
        all_recipients_rules = [x for x in self.objectValues()
                                if getattr(x, 'getRecipients', 0)]
        if recipients_rule_type is None:
            return all_recipients_rules
        else:
            return [x for x in all_recipients_rules \
                    if x.meta_type == recipients_rule_type]

    def getParentContainer(self):
        """Return the subscription parent container
        """
        return aq_parent(aq_inner(self))

InitializeClass(Subscription)

def addSubscription(self, id=None, title='', REQUEST=None):
    """Add a Subscriptions object"""

    if id is None:
        id = self.computeId()

    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = Subscription(id, title=title)
    self._setObject(id, ob)

    subscription = getattr(self, id)

    # Explicit recipients rules (Compulsory for subscriptions)
    subscription.manage_addProduct[
        'CPSSubscriptions'].addExplicitRecipientsRule()

    # Mail Notification is default notification right now.
    subscription.manage_addProduct[
        'CPSSubscriptions'].addMailNotificationRule()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main')
    return subscription

# Copyright (C) 2004-2008 Nuxeo SAS <http://nuxeo.com>
# Copyright (C) 2004 CGEY <http://cgey.com>
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

__author__ = "Julien Anguenot <mailto:ja@nuxeo.com>"

""" Subscription container class definition

This is a placefull subscription container holding the subscripions
configuration.
"""

from logging import getLogger
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent

from Globals import InitializeClass
from Globals import MessageDialog

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import ModifyPortalContent

from Products.CPSCore.CPSBase import CPSBaseFolder

from Products.CPSSubscriptions.permissions import CanSubscribe
from Products.CPSSubscriptions.permissions import ManageSubscriptions

logger = getLogger('CPSSubscriptions.SubscriptionContainer')

class SubscriptionContainer(CPSBaseFolder):
    """ Subscription container

    Placeful Object containing subscription information.
    """

    meta_type = 'CPS PlaceFull Subscription Container'
    portal_type = meta_type

    security = ClassSecurityInfo()

    _properties = CPSBaseFolder._properties + \
                  ({'id': 'notify_local_only',
                    'type': 'boolean',
                    'mode': 'w',
                    'label': 'Notify Local Only'},
                   {'id': 'notify_no_local',
                    'type': 'boolean',
                    'mode': 'w',
                    'label': 'Notify No Local'},
                   {'id': 'subscription_allowed',
                    'type': 'boolean',
                    'mode':'w',
                    'label' : 'Subscription Allowed ?'},
                   {'id': 'unsubscription_allowed',
                    'type': 'boolean',
                    'mode':'w',
                    'label' : 'Unsubscription Allowed ?'},
                   {'id': 'anonymous_subscription_allowed',
                    'type': 'boolean',
                    'mode':'w',
                    'label' : 'Anonymous Subscription Allowed ?'},
                   {'id': 'mfrom',
                    'type':'string',
                    'mode':'w',
                    'label' : 'Mail From'},
                   {'id': 'lang',
                    'type':'string',
                    'mode':'w',
                    'label' : 'Language'},
                   {'id': 'user_modes',
                    'type':'string',
                    'mode':'r',
                    'label' :
                    'What frequence the user choose for its notifications'},
                   )

    notify_local_only = 0
    notify_no_local = 0
    subscription_allowed = 1
    unsubscription_allowed = 1
    anonymous_subscription_allowed = 0
    mfrom = ''
    lang  = 'en'
    user_modes = {}

    def __init__(self, id, title=''):
        """ Constructor

        Parent's class and attributes intialization
        """
        CPSBaseFolder.__init__(self, id, title=title)
        self.notify_local_only = 0
        self.notify_no_local = 0
        self.subscription_allowed = 1
        self.unsubscription_allowed = 1
        self.anonymous_subscription_allowed = 0
        self.mfrom = ''
        self.lang = 'en'
        self.user_modes = {}

    security.declarePublic('getMailFrom')
    def getMailFrom(self, with_user=True):
        """Returns the email address that's stored at container level.
        See #1925 for more detail.
        """
        return self.mfrom

    def getLanguage(self):
        """Returns the subscription language

        Will be use when sending emails to the mailing list
        """
        # XXX not used yet
        return self.lang

    security.declarePublic('isNotificationLocalOnly')
    def isNotificationLocalOnly(self):
        """Are notifications local only ?

        Is the notifications only for user having local roles in here
        Do not infer with merged local roles.
        """
        return self.notify_local_only

    security.declarePublic('isNotificationNoLocal')
    def isNotificationNoLocal(self):
        """Are notifications no local ?

        Is the notifications only for users having local roles
        within the sub-folders
        """
        return self.notify_no_local

    security.declarePublic('isSubscriptionAllowed')
    def isSubscriptionAllowed(self):
        """Is Subscription Allowed ?
        """
        membership_tool = getToolByName(self, 'portal_membership')
        if membership_tool.isAnonymousUser():
            return (self.subscription_allowed and \
                    self.anonymous_subscription_allowed)
        return self.subscription_allowed

    security.declarePublic('isUnSubscriptionAllowed')
    def isUnSubscriptionAllowed(self):
        """Is UnSubscription Allowed ?

        Usefull to provide the possibility to users to unsubscribe if
        they are computed as recipients based on their roles
        """
        return self.unsubscription_allowed

    security.declarePublic('isAnonymousSubscriptionAllowed')
    def isAnonymousSubscriptionAllowed(self):
        """Is Anonymous Subscription Allowed ?
        """
        return self.anonymous_subscription_allowed

    security.declareProtected(ManageSubscriptions, 'updateProperties')
    def updateProperties(self, **kw):
        """ Update Subscription Folder Properties

        Using kw parameter dictionnnary holding the properties
        """
        if kw is not None:
            for prop in kw.keys():
                if hasattr(self, prop):
                    setattr(self, prop, kw[prop])
        perms = []

        # Update permissions
        if self.subscription_allowed and 1:
            perms.append('Authenticated')
        if self.anonymous_subscription_allowed and 1:
            perms.append('Anonymous')
        self.changePermissions(perms=perms)
        self.reindexObject()

    security.declareProtected(ManageSubscriptions, 'changePermissions')
    def changePermissions(self, perms=[]):
        """Change CanSubscribe permissions
        """
        new_perms = {
            CanSubscribe : perms
            }

        for perm, roles in new_perms.items():
            self.manage_permission(perm, roles, 1)
        try:
            self.reindexObjectSecurity()
        except Exception, inst:
            logger.info("Some permissions may not be present anymore: %s" % inst)

    security.declareProtected(CanSubscribe, 'addSubscription')
    def addSubscription(self, id=None):
        """Add a subscription object within the subscription folder
        """
        return self.manage_addProduct['CPSSubscriptions'].addSubscription(id=id)

    security.declarePublic('getSubscriptionById')
    def getSubscriptionById(self, subscription_id=''):
        """Return a susbcription object given an id

        If it doesn't exist then create it
        """
        subtool = getToolByName(self, 'portal_subscriptions')
        subscription_prefix = subtool.getSubscriptionObjectPrefix()

        if not subscription_id.startswith(subscription_prefix):
            subscription_id = subscription_prefix + subscription_id

        subscription = getattr(self, subscription_id, None)

        # Cope with the None case : the subscription doesn't exist yet
        if (subscription is None and
            _checkPermission(ManageSubscriptions, self)):
            subscription = self.addSubscription(subscription_id)
        return subscription

    security.declarePublic('getSubscriptions')
    def getSubscriptions(self):
        """ Get all Subscriptions contained in here.
        """
        # XXX : find sthg else to find these subscription objects
        return [x for x in self.objectValues()
                if getattr(x, 'getFilterEventTypes', False)]

    security.declareProtected(CanSubscribe, 'updateUserMode')
    def updateUserMode(self, email, mode):
        """Update user mode
        """
        # In case it has been changed in ZMI with older
        # CPSSubscriptions revision
        if not isinstance(self.user_modes, dict):
            self.user_modes = {}
        user_modes = self.user_modes
        if email and mode:
            user_modes[email] = mode
        self.user_modes = user_modes

    security.declareProtected(CanSubscribe, 'getUserMode')
    def getUserMode(self, email):
        """Return the mode corresponding to a given email
        """
        # In case it has been changed in ZMI with older
        # CPSSubscriptions revision
        if not isinstance(self.user_modes, dict):
            self.user_modes = {}
        if email in self.user_modes.keys():
            return self.user_modes[email]
        # No mode == real time (default value)
        return 'mode_real_time'

InitializeClass(SubscriptionContainer)

def addSubscriptionContainer(self, id=None, REQUEST=None):
    """Add a Subscription Folder Container
    """

    subtool = getToolByName(self, 'portal_subscriptions')
    id = subtool.getSubscriptionContainerId()

    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = SubscriptionContainer(id, title='Placefull Subscription Container')
    self._setObject(id, ob)

    subscription_container = getattr(self, id)

    # Set 'CanSubscribe' permission to roles mapping
    subscription_container.updateProperties()

    # Let's create event subscriptions mapping the context.
    # These information are know by tool site.
    # We need to create them right now for the subscriptions

    parent = aq_parent(aq_inner(subscription_container))
    events_in_context = subtool.getEventsFromContext(parent)

    for event in events_in_context.keys():
        id = 'subscription__' + event
        title = 'Event '+ event # i18n
        subscription_container.manage_addProduct[
            'CPSSubscriptions'].addSubscription(id, title)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main')

# Copyright (C) 2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (C) 2004 CGEY <http://cgey.com>
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

""" Subscription Container Folder Class

This is a placefull subscription container holding the configuration.
"""

from Globals import InitializeClass, MessageDialog
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName

class SubscriptionContainer(PortalFolder):
    """ Subscription Container Class

    Placefull Object containing subscription information.
    """

    meta_type = 'CPS PlaceFull Subscription Container'
    portal_type = meta_type

    security = ClassSecurityInfo()

    _properties = PortalFolder._properties + \
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
                   )

    notify_local_only = 0
    notify_no_local = 0
    subscription_allowed = 0
    unsubscription_allowed = 0
    anonymous_subscription_allowed = 0
    mfrom = ''
    lang  = 'en'

    def __init__(self, id, title=''):
        """ Constructor

        Parent's class and attributes intialization
        """
        PortalFolder.__init__(self, id, title=title)
        self.notify_local_only = 0
        self.notify_no_local = 0
        self.subscription_allowed = 0
        self.unsubscription_allowed = 0
        self.anonymous_subscription_allowed = 0
        self.mfrom = ''
        self.lang = 'en'

    security.declarePublic('getMailFrom')
    def getMailFrom(self):
        """Returns the default email address from for the emails
        that are going to be sent by this container

        The email address used by default is the email address of the portal
        administrator.
        """
        if not self.mfrom:
            self.mfrom = self.portal_properties.email_from_address
        return self.mfrom

    def getLanguage(self):
        """Returns the subscription language

        Will be use when sending emails to the mailing list
        """
        return self.lang

    security.declarePublic("isNotificationLocalOnly")
    def isNotificationLocalOnly(self):
        """Are notifications local only ?

        Is the notifications only for user having local roles in here
        Do not infer with merged local roles.
        """
        return self.notify_local_only

    security.declarePublic("isNotificationNoLocal")
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

    security.declareProtected(ModifyPortalContent, "updateProperties")
    def updateProperties(self, **kw):
        """ Update Subscription Folder Properties

        Using kw parameter dictionnnary holding the properties
        """
        if kw is not None:
            for prop in kw.keys():
                if hasattr(self, prop):
                    setattr(self, prop, kw[prop])

    security.declarePublic("getSubscriptions")
    def getSubscriptions(self):
        """ Get all Subscriptions contained in here.
        """
        # XXX : find sthg else to find these subscription objects
        return [x for x in self.objectValues() if getattr(x,
                                                          'getFilterEventTypes',
                                                          0)]

InitializeClass(SubscriptionContainer)

def addSubscriptionContainer(self, id=None, REQUEST=None):
    """ Add a Subscription Folder Container """

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

    #
    # Let's create event subscriptions mapping the context.
    # These information are know tool site.
    # We need to create them right now for the subscriptions
    #

    parent = aq_parent(aq_inner(subscription_container))
    events_in_context = subtool.getEventsFromContext(parent)

    for event in events_in_context.keys():
        id = 'subscription__' + event
        title = 'Event '+ event # i18n
        subscription_container.manage_addProduct['CPSSubscriptions'].addSubscription(id, title)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main')

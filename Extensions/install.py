# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2004 CGEY <http://cgey.com>
# Copyright (c) 2004 Ministère de L'intérieur (MISILL)
#               <http://www.interieur.gouv.fr/>
# Author: Julien Anguenot <ja@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

""" CPSSubscriptions Installer

Installer/Updater fot the CPSSubscriptions component.
"""

from zLOG import LOG, INFO, DEBUG

import os, sys

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent, setDefaultRoles
from Products.CPSDefault.Installer import BaseInstaller

from Products.CPSSubscriptions.CPSSubscriptionsPermissions import ManageSubscriptions

SECTIONS_ID = 'sections'
WORKSPACES_ID = 'workspaces'
SKINS = (
    ('cps_subscriptions', 'Products/CPSSubscriptions/skins/cps_subscriptions',),
    ('cps_subscriptions_installer', 'Products/CPSSubscriptions/skins/cps_subscriptions_installer',),
    )

class CPSSubscriptionsInstaller(BaseInstaller):
    """ Installer class for CPS Subscriptions component

    Intended to be use as an Installer/Updater tool.
    """

    product_name = 'CPSSubscriptions'

    def install(self):
        """ Installs the compulsory elements.

        Calling feature methods.
        """

        self.log("Install/Update : CPSSubscriptions Product")
        self.setupSkins(SKINS)
        self.setupSubscriptionsTool()
        self.installActions()
        self.installNewPermissions()
        self.setupSubscriber()
        self.setupTranslations()
        self.setupCatalogSpecifics()
        self.log("End of Install/Update : CPSSubscriptions Product")

    def setupSubscriptionsTool(self):
        """ Installs the subscriptions tool

        id : portal_subscriptions
        """

        self.log("Checking CPS Subscriptions Tool")
        if not getToolByName(self.portal, 'portal_subscriptions', 0):
            self.log(" Creating CPS Subscriptions Tool (portal_subscriptions)")
            self.portal.manage_addProduct["CPSSubscriptions"].manage_addTool(\
                                      'Subscriptions Tool')
            portal_subscriptions = getToolByName(self.portal, 'portal_subscriptions')
	    portal_subscriptions.setupEvents()

    def installNewPermissions(self):
        """Installs new subscriptions dedicated permissions
        """

        subscription_workspace_perms = {
            ManageSubscriptions : ['Manager', 'WorkspaceManager'],
            }
        subscription_sections_perms = {
            ManageSubscriptions : ['Manager', 'SectionManager'],
            }

        for perm, roles in subscription_workspace_perms.items():
            self.portal[WORKSPACES_ID].manage_permission(perm, roles, 0)
        for perm, roles in subscription_workspace_perms.items():
            self.portal[SECTIONS_ID].manage_permission(perm, roles, 0)

    def installActions(self):
        """ Installs new actions permitting to manage notifications
        within CPS, to manage its subscriptions and to subscribe.

        Action category : folder
        """

        #
        # Cleaning actions
        #

        actiondelmap = {
            'portal_actions': ('folder_notifications',
                               'folder_subscribe',
                               'my_subscriptions')
            }
        for tool, actionids in actiondelmap.items():
            actions = list(self.portal[tool]._actions)
            new_actions = []
            for ac in actions:
                id = ac.id
                if id not in actionids:
                    new_actions.append(ac)
                self.portal[tool]._actions = new_actions

        #
        # ACTION : Manage subscriptions
        # category : folder
        #

        self.portal['portal_actions'].addAction(
            id='folder_notifications',
            name='action_folder_notifications',
            action='string: ${object_url}/folder_notifications_form',
            condition="python:hasattr(object, 'portal_type') and object.portal_type in portal.portal_subscriptions.getContainerPortalTypes() and object.portal_type != 'Portal'",
            permission=(ManageSubscriptions,),
            category='folder',
            visible=1)
        self.log(" Added Action folder Notifications")

        #
        # ACTION : Manage my subscriptions
        # category : user
        #

        self.portal['portal_actions'].addAction(
            id='my_subscriptions',
            name='action_my_subscriptions',
            action='string: ${portal_url}/manage_my_subscriptions_form',
            condition="python:not portal.portal_membership.isAnonymousUser()",
            permission=(View,),
            category='user',
            visible=1)
        self.log(" Added Action My Subscriptions")

        #
        # ACTION : Subscribe
        # category : folder
        #

        # FIXME : cheking if subscription allowed in the context

        self.portal['portal_actions'].addAction(
            id='folder_subscribe',
            name='action_folder_subscribe',
            action='string: ${object_url}/folder_subscribe_form',
            condition="python:hasattr(object, 'portal_type') and \
            object.portal_type != 'Portal' and \
            object.portal_type in portal.portal_subscriptions.getSubscribablePortalTypes() and \
            hasattr(object, portal.portal_subscriptions.getSubscriptionContainerId()) and \
            getattr(object, portal.portal_subscriptions.getSubscriptionContainerId()).isSubscriptionAllowed()" ,
            permission=(View,),
            category='folder',
            visible=1)
        self.log(" Added Action folder Subscribe")

    def setupSubscriber(self):
        """ Adds portal_subscriptions as subscriber of portal_eventservice

        notification method : event
        """

        portal_eventservice = getToolByName(self.portal,
                                            'portal_eventservice',
                                            0)
        if portal_eventservice:
            objs = portal_eventservice.objectValues()
            subscribers = []
            for obj in objs:
                subscribers.append(obj.subscriber)
            if 'portal_subscriptions' not in subscribers:
                self.log("Adding portal_subscribtions as subscriber")
                portal_eventservice.manage_addSubscriber(
                    subscriber='portal_subscriptions',
                    action='event',
                    meta_type='*',
                    event_type='*',
                    notification_type='synchronous')
            else:
                self.log("portal_subscribtions already subscriber")
        else:
            raise ('DEPENDENCY ERROR : portal_eventservice')

    def setupCatalogSpecifics(self):
        """Setup specifics catalog thingies.

        The point in here is being able to get where a given members/email has
        some subscriptions
        """

        self.log("Setting some specifics on catalog")

        catalog = getToolByName(self.portal, 'portal_catalog')
        indexes = {
            'getSubscriptions' : 'FieldIndex',
            }
        metadata = [
            'getSubscriptions',
            ]

        for ix, typ in indexes.items():
            if ix in catalog.Indexes.objectIds():
                self.log("  %s: ok" % ix)
            else:
                prod = catalog.Indexes.manage_addProduct['PluginIndexes']
                constr = getattr(prod, 'manage_add%s' % typ)
                constr(ix)
                self.log("  %s: added" % ix)
        for md in metadata:
            if md in catalog.schema():
                self.log("  %s: ok" % md)
            else:
                catalog.addColumn(md)
                self.log("  %s: added" % md)

        self.log("End if setting some specifics on catalog")

###############################################
# __call__
###############################################

def install(self):
    """Installation is done here.

    Called by an external method for instance.
    """
    installer = CPSSubscriptionsInstaller(self)
    installer.install()
    return installer.logResult()

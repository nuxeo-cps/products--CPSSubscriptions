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
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CPSDefault.Installer import BaseInstaller

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
        self.setupSubscriber()
        self.setupEvents()
        self.setupTranslations()
        self.log("End of Install/Update : CPSSubscriptions Product")

    def setupSubscriptionsTool(self):
        """ Installs the subscriptions tool

        id : portal_subscriptions
        """

        self.log("Checking CPS Subscriptions Tool")
        if getToolByName(self.portal, 'portal_subscriptions', 0):
            self.log("Deleting existing CPS Subscriptions Tool")
            self.portal.manage_delObjects(['portal_subscriptions',])
        self.log(" Creating CPS Subscriptions Tool (portal_subscriptions)")
        self.portal.manage_addProduct["CPSSubscriptions"].manage_addTool(\
                'Subscriptions Tool')

    def installActions(self):
        """ Installs a new action permitting to manage notifications
        within CPS.

        Action category : folder
        """

        action_found = 0
        for action in self.portal['portal_actions'].listActions():
            if action.id == 'folder_notifications':
                action_found = 1
        if not action_found:
            self.portal['portal_actions'].addAction(
                id='folder_notifications',
                name='action_folder_notifications',
                action='string: ${folder_url}/folder_notifications_form',
                condition="python:hasattr(object, 'portal_type') and object.portal_type not in ('Section', 'Portal')",
                permission=(ModifyPortalContent,),
                category='folder',
                visible=1)
            self.log(" Added Action folder Notifications")

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

    def setupEvents(self):
        """ Setup events on which to react
        """

        subscriptions_tool = getToolByName(self.portal,
                                           'portal_subscriptions',
                                           0)

        if subscriptions_tool:
            mapping_context_events = self.portal.getEvents()
            for context in mapping_context_events.keys():
                for event_id in mapping_context_events[context].keys():
                    subscriptions_tool.manage_addEventType(context,
                                                           event_id,
                                                           mapping_context_events[
                        context][event_id])
        else:
            raise "Hum,....portal_subscriptions disapears on the middle of the install process..."

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

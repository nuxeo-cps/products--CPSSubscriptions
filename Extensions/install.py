# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Copyright (C) 2003 CGEY <http://cgey.com>
# Copyright (c) 2003 Ministère de L'intérieur (MISILL)
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

XXX : comments

"""

from zLOG import LOG, INFO, DEBUG

import os, sys
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CPSDefault.Installer import BaseInstaller

SECTIONS_ID = 'sections'
WORKSPACES_ID = 'workspaces'
SKINS = (
    ('cps_subscriptions', 'Products/CPSSubscriptions/skins/cps_subscriptions',),
    )

class CPSSubscriptionsInstaller(BaseInstaller):
    """ Installer class for CPS Subscriptions module

    XXX : comments
    """

    product_name = 'CPSSubscriptions'

    def install(self):
        """
        Calling feature methods.
        """
        self.log("Setup/Intialization : CPSSubscriptions Product")
        self.setupSkins(SKINS)
        self.setupSubscriptionsTool()
        self.installActions()
        self.setupTranslations()
        self.log("End of Setup/Intialization : CPSSubscriptions Product")

    def setupSubscriptionsTool(self):
        """
        Check the subscriptions tool install.
        """
        self.log("Installing CPS Subscriptions Tool")
        if getattr(self.portal, 'portal_subscriptions', None) :
            self.portal.manage_delObjects(['portal_subscriptions',])
        self.log(" Creating CPS Subscriptions Tool (portal_subscriptions)")
        self.portal.manage_addProduct["CPSSubscriptions"].manage_addTool(\
                'Subscriptions Tool')

    def installActions(self):
        """
        Add new folder action
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
                condition='',
                permission=(ModifyPortalContent,),
                category='folder',
                visible=1)
            self.log(" Added Action folder Notifications")

class CMFSubscriptionsInstaller(CPSSubscriptionsInstaller):
    pass

###############################################
# __call__
###############################################

def install(self):
    """
    XXX : comments
    """
    installer = CPSSubscriptionsInstaller(self)
    installer.install()
    return installer.logResult()

def cmfinstall(self):
    installer = CMFSubscriptionsInstaller()
    installer.install()
    return installer.logResult()

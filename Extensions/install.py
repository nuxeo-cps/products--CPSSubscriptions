# -*- codin: ISO-8859-15 -*-
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

from Products.ExternalMethod.ExternalMethod import ExternalMethod

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent, \
     setDefaultRoles
from Products.CPSInstaller.CPSInstaller import CPSInstaller

from Products.CPSSubscriptions.CPSSubscriptionsPermissions import \
     ManageSubscriptions, CanSubscribe, ViewMySubscriptions

SECTIONS_ID = 'sections'
WORKSPACES_ID = 'workspaces'
SKINS = {
    'cps_subscriptions' :
    'Products/CPSSubscriptions/skins/cps_subscriptions',
    'cps_subscriptions_installer':
    'Products/CPSSubscriptions/skins/cps_subscriptions_installer',
    }

class CPSSubscriptionsInstaller(CPSInstaller):
    """ Installer class for CPS Subscriptions component

    Intended to be use as an Installer/Updater tool.
    """

    product_name = 'CPSSubscriptions'

    def install(self):
        """ Installs the compulsory elements.

        Calling feature methods.
        """

        self.log("Install/Update : CPSSubscriptions Product")
        self.verifySkins(SKINS)
        self.resetSkinCache()
        self.setupSubscriptionsTool()
        self.installActions()
        self.installNewPermissions()
        self.setupSubscriber()
        self.setupRelevantLocalRoles()
        self.verifyNewPermissions()
        self.setupTranslations()
        self.setupCatalogSpecifics()
        self.finalize()
        self.reindexCatalog()
        self.insallUpdateExMethod()
        self.log("End of Install/Update : CPSSubscriptions Product")

    def setupSubscriptionsTool(self):
        """ Installs the subscriptions tool

        id : portal_subscriptions
        """

        self.log("Checking CPS Subscriptions Tool")
        if getToolByName(self.portal, 'portal_subscriptions', None) is None:
            self.log(" Creating CPS Subscriptions Tool (portal_subscriptions)")
            self.portal.manage_addProduct['CPSSubscriptions'].manage_addTool('Subscriptions Tool')
        else:
            # XXX waiting for the CPSIO import / export
            # FIXME !!!
            # Save the current portal_subscriptions properties
            # tmp for compatibility with version < 0.10

            tool = getToolByName(self.portal, 'portal_subscriptions')

            if getattr(tool, 'notification_scheduling_table', None) is None:

                notify_hidden_object = getattr(tool,
                                               'notify_hidden_object',
                                               0)
                mapping_context_events = getattr(tool,
                                                 'mapping_context_events',
                                                 {})
                mapping_event_email_content = getattr(tool,
                                                      'mapping_event_email_content',
                                                      {})
                event_default_email_title = getattr(tool,
                                                    'event_default_email_title',
                                                    '')
                event_default_email_body = getattr(tool,
                                                   'event_default_email_body',
                                                   '')
                event_error_email_body = getattr(tool,
                                                 'event_error_email_body',
                                                 '')
                subscribe_confirm_email_title = getattr(tool,
                                                        'subscribe_confirm_email_title',
                                                        '')
                subscribe_confirm_email_body = getattr(tool,
                                                       'subscribe_confirm_email_body',
                                                       '')
                subscribe_welcome_email_title = getattr(tool,
                                                        'subscribe_welcome_email_title',
                                                        '')
                subscribe_welcome_email_body = getattr(tool,
                                                       'subscribe_welcome_email_body',
                                                       '')
                unsubscribe_confirm_email_title = getattr(tool,
                                                          'unsubscribe_confirm_email_title',
                                                          '')
                unsubscribe_confirm_email_body = getattr(tool,
                                                         'unsubscribe_confirm_email_body',
                                                         '')
                unsubscribe_email_title = getattr(tool,
                                                  'unsubscribe_email_title',
                                                  '')
                unsubscribe_email_body = getattr(tool,
                                                 'unsubscribe_email_body',
                                                 '')
                render_content_for_portal_types = getattr(tool,
                                                          'render_content_for_portal_types',
                                                          [])
                render_content_for_events = getattr(tool,
                                                    'render_content_for_events',
                                                    [])
                notification_scheduling_table = getattr(tool,
                                                        'notification_scheduling_table',
                                                        {})
                # Delete and create a new tool
                self.portal.manage_delObjects(['portal_subscriptions'])
                self.portal.manage_addProduct['CPSSubscriptions'].manage_addTool('Subscriptions Tool')
                # Restore values
                tool = getToolByName(self.portal, 'portal_subscriptions')

                tool.notify_hidden_object = notify_hidden_object
                tool.mapping_context_events = mapping_context_events
                tool.mapping_event_email_content = mapping_event_email_content
                tool.event_default_email_title = event_default_email_title
                tool.event_default_email_body = event_default_email_body
                tool.event_error_email_body = event_error_email_body
                tool.subscribe_confirm_email_title = subscribe_confirm_email_title
                tool.subscribe_confirm_email_body = subscribe_confirm_email_body
                tool.subscribe_welcome_email_title = subscribe_welcome_email_title
                tool.subscribe_welcome_email_body = subscribe_welcome_email_body
                tool.unsubscribe_confirm_email_title = unsubscribe_confirm_email_title
                tool.unsubscribe_confirm_email_body = unsubscribe_confirm_email_body
                tool.unsubscribe_email_title = unsubscribe_email_title
                tool.unsubscribe_email_body = unsubscribe_email_body
                tool.render_content_for_portal_types = render_content_for_portal_types
                tool.render_content_for_events = render_content_for_events
                tool.notification_scheduling_table = notification_scheduling_table

        self.portal.portal_subscriptions.setupEvents()

    def installNewPermissions(self):
        """Installs new subscriptions dedicated permissions
        """

        subscription_workspace_perms = {
            ManageSubscriptions : ['Manager', 'WorkspaceManager', 'ForumModerator'],
            }
        subscription_sections_perms = {
            ManageSubscriptions : ['Manager', 'SectionManager', 'ForumModerator'],
            }

        for perm, roles in subscription_workspace_perms.items():
            self.portal[WORKSPACES_ID].manage_permission(perm, roles, 1)
        for perm, roles in subscription_sections_perms.items():
            self.portal[SECTIONS_ID].manage_permission(perm, roles, 1)

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
            condition="python:hasattr(object, 'portal_type') and object.portal_type in portal.portal_subscriptions.getContainerPortalTypes()",
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
            permission=(ViewMySubscriptions,),
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


    def verifyNewPermissions(self):
        """Verify New Roles
        """

        self.setupPortalPermissions({
            CanSubscribe : ['Manager',
                            ],
            ManageSubscriptions : ['Manager',
                                   ],
            ViewMySubscriptions : ['Manager',
                                   'Member'],
            })

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

    def insallUpdateExMethod(self):
        """Install an external method that permits to upgrade
        latest changes
        """
        self.log("Installing external method to update existing instance")
        cpsubscriptions_upgrade_old_instance = ExternalMethod(
            'UPGRADE SUBSCRIPTIONS',
            'WARNING: USE ONLY IF YOU KNOW WHAT YOU ARE DOING',
            'CPSSubscriptions.install',
            'updateContainers')

        if 'cpsubscriptions_upgrade_old_instance' not in self.portal.objectIds():
            self.portal._setObject('cpsubscriptions_upgrade_old_instance',
                                   cpsubscriptions_upgrade_old_instance)

    def setupRelevantLocalRoles(self):
        """portal_subscriptions is going to hold information about the relevant
        local roles within a given context so that we can propose good local
        Roles depending on this one
        """

        # Skins
        context_local_roles_mapping = self.portal.getCPSSubscriptionsLocalRolesMapping()
        subtool = getToolByName(self.portal, 'portal_subscriptions')

        # Setting by area
        for area in context_local_roles_mapping.keys():
            subtool.setLocalRolesArea(area=area, value=context_local_roles_mapping[area])

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

def updateContainers(self):
    """Update container because of the incompatible
    changed made recently. Use that from an external method
    for your already existing projects
    """

    log = []
    pr = log.append

    pr("UPGRADE CPSSubscriptions old instance")
    subtool = self.portal_subscriptions

    # Fetching all the containers on the portal
    catalog = self.portal_catalog
    portal_type = 'CPS PlaceFull Subscription Container'
    containers = catalog.searchResults({'portal_type':
                                            portal_type,})
    containers = [x.getObject() for x in containers]

    for container in containers:
        pr("Checking container at %s" %container.absolute_url())
        #
        # Permissions updating
        #

        container.updateProperties()

        #
        # Now removing existing subscription
        # Only for explict subscribersà
        # HUOM !! You're gonna loose all your explicit subscriptions
        # Be sure you know you're doing
        #

        explicit_id = subtool.getExplicitRecipientsRuleId()
        for subscription in container.getSubscriptions():
            explicit = getattr(subscription, explicit_id, None)
            if explicit is not None:
                explicit.members = []
                explicit.emails = []
                explicit.emails_subscribers = []
                explicit.emails_pending_add = []
                explicit.emails_pending_delete = []

    pr("DONE")
    return '\n'.join(log)

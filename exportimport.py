# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author:
# M.-A. Darche <madarche@nuxeo.com>
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
"""CPSSubscriptions Tool XML Adapter.
"""

from zope.component import adapts
from zope.interface import implements

from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers

from Products.CMFCore.utils import getToolByName

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from Products.CPSUtil.genericsetup import StrictTextElement

from Products.CPSSubscriptions.interfaces import ISubscriptionsTool


TOOL = 'portal_subscriptions'
NAME = 'subscriptions'

def exportSubscriptionsTool(context):
    """Export subscriptions tool and subobjects as a set of XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL, None)
    if tool is None:
        logger = context.getLogger(NAME)
        logger.info("Nothing to export.")
        return
    exportObjects(tool, '', context)

def importSubscriptionsTool(context):
    """Import subscriptions tool and subobjects from XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL)
    importObjects(tool, '', context)

    # FIXME
    try:
        # Setting up events on which to react
        tool.setupEvents()
    except AttributeError:
        pass

    # Setting up default mappings.
    # The tool is going to hold information about the relevant local roles
    # within a given context so that we can propose good local Roles depending
    # on this one.
    try:
        roles_map = site.getCPSSubscriptionsLocalRolesMapping()
    except AttributeError:
        pass
    else:
        for area in roles_map.keys():
            tool.setLocalRolesArea(area=area, value=roles_map[area])

class SubscriptionsToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                                  PropertyManagerHelpers):
    """XML importer and exporter for SubscriptionsTool.
    """

    adapts(ISubscriptionsTool, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME
    name = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())
        node.appendChild(self._extractContextEvents())
        node.appendChild(self._extractAreaContextRoles())
        node.appendChild(self._extractEventDefaultMessages())
        node.appendChild(self._extractEventMessages())

        self._logger.info("Subscriptions tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeObjects()
            self._purgeContextEvents()
            self._purgeAreaContextRoles()
            self._purgeEventDefaultMessages()
            self._purgeEventMessages()

        self._initProperties(node)
        self._initObjects(node)
        self._initContextEvents(node)
        self._initAreaContextRoles(node)
        self._initEventDefaultMessages(node)
        self._initEventMessages(node)

        self._logger.info("Subscriptions tool imported.")

    def _extractContextEvents(self):
        fragment = self._doc.createDocumentFragment()
        mapping_context_events = self.context.mapping_context_events
        portal_types = mapping_context_events.keys()
        portal_types.sort()
        for portal_type in portal_types:
            node = self._doc.createElement('context-events')
            node.setAttribute('portal_type', portal_type)
            event_labels = mapping_context_events[portal_type]
            event_ids = event_labels.keys()
            event_ids.sort()
            for event_id in event_ids:
                event_label = event_labels[event_id]
                child = self._doc.createElement('event')
                child.setAttribute('id', event_id)
                text = self._doc.createTextNode(event_label)
                child.appendChild(text)
                node.appendChild(child)
            fragment.appendChild(node)
        return fragment

    def _purgeContextEvents(self):
        pass

    def _initContextEvents(self, node):
        pass

    def _extractAreaContextRoles(self):
        fragment = self._doc.createDocumentFragment()
        mapping_areas = self.context.mapping_local_roles_context
        areas = mapping_areas.keys()
        areas.sort()
        for area in areas:
            area_node = self._doc.createElement('area')
            area_node.setAttribute('portal_type', area)
            context_roles = mapping_areas[area]
            portal_types = context_roles.keys()
            portal_types.sort()
            for portal_type in portal_types:
                type_node = self._doc.createElement('context-roles')
                type_node.setAttribute('portal_type', portal_type)
                role_labels = context_roles[portal_type]
                roles = role_labels.keys()
                roles.sort()
                for role in roles:
                    role_node = self._doc.createElement('role')
                    role_node.setAttribute('id', role)
                    role_label = role_labels[role]
                    text_node = self._doc.createTextNode(role_label)
                    role_node.appendChild(text_node)
                    type_node.appendChild(role_node)
                area_node.appendChild(type_node)
            fragment.appendChild(area_node)
        return fragment

    def _purgeAreaContextRoles(self):
        pass

    def _initAreaContextRoles(self, node):
        pass

    def _extractEventDefaultMessages(self):
        tool = self.context
        fragment = self._doc.createDocumentFragment()
        for event_id, prefix in (
            ('(default)', 'getDefaultMessage'),
            ('(error)', 'getErrorMessage'),
            ('(subscribe-confirm)', 'getSubscribeConfirmEmail'),
            ('(subscribed)', 'getSubscribeWelcomeEmail'),
            ('(unsubscribe-confirm)', 'getUnSubscribeConfirmEmail'),
            ('(unsubscribed)', 'getUnSubscribeEmail'),
            ):
            if event_id != '(error)':
                subject = getattr(tool, prefix+'Title')()
            else:
                subject = None
            body = getattr(tool, prefix+'Body')()
            node = self._extractOneMessage(event_id, subject, body)
            fragment.appendChild(node)
        return fragment

    def _purgeEventDefaultMessages(self):
        pass

    def _initEventDefaultMessages(self, node):
        pass

    def _extractEventMessages(self):
        fragment = self._doc.createDocumentFragment()
        tool = self.context

        default_subject = tool.getDefaultMessageTitle()
        default_body = tool.getDefaultMessageBody()

        event_ids = tool.getRecordedEvents()
        event_ids.sort()
        for event_id in event_ids:
            subject = tool.getDefaultMessageTitle(event_id)
            body = tool.getDefaultMessageBody(event_id)
            if subject == default_subject and body == default_body:
                # Will use the default
                continue

            node = self._extractOneMessage(event_id, subject, body)
            fragment.appendChild(node)

        return fragment

    def _extractOneMessage(self, event_id, subject, body):
        node = self._doc.createElement('message')
        node.setAttribute('event_id', event_id)

        if subject is not None:
            subject_node = self.createStrictTextElement('subject')
            text = self._doc.createTextNode(subject.strip())
            subject_node.appendChild(text)
            node.appendChild(subject_node)

        body_node = self.createStrictTextElement('body')
        text = self._doc.createTextNode(body)
        body_node.appendChild(text)
        node.appendChild(body_node)

        return node

    def _purgeEventMessages(self):
        pass

    def _initEventMessages(self, node):
        pass

    def createStrictTextElement(self, tagName):
        e = StrictTextElement(tagName)
        e.ownerDocument = self._doc
        return e

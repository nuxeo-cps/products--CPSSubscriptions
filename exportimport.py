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

from Products.CMFCore.utils import getToolByName

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from Products.CPSUtil.genericsetup import StrictTextElement
from Products.CPSUtil.genericsetup import getExactNodeText
from Products.CPSUtil.PropertiesPostProcessor import (
    PostProcessingPropertyManagerHelpers)

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

class SubscriptionsToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                                  PostProcessingPropertyManagerHelpers):
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
        node.appendChild(self._extractDefaultEventMessages())
        node.appendChild(self._extractEventMessages())

        self._logger.info("Subscriptions tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        self.context._p_changed = 1

        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeObjects()
            self._purgeContextEvents()
            self._purgeAreaContextRoles()
            self._purgeDefaultEventMessages()
            self._purgeEventMessages()

        self._initProperties(node)
        self._initObjects(node)
        self._initContextEvents(node)
        self._initAreaContextRoles(node)
        self._initDefaultEventMessages(node)
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
        self.context.mapping_context_events = {}

    def _initContextEvents(self, node):
        mapping_context_events = self.context.mapping_context_events
        for child in node.childNodes:
            if child.nodeName != 'context-events':
                continue
            portal_type = str(child.getAttribute('portal_type'))
            event_labels = mapping_context_events.setdefault(portal_type, {})
            if self._convertToBoolean(child.getAttribute('purge') or 'False'):
                # purge existing labels
                event_labels = mapping_context_events[portal_type] = {}

            for subnode in child.childNodes:
                if subnode.nodeName != 'event':
                    continue
                event_id = str(subnode.getAttribute('id'))
                event_label = self._getNodeText(subnode)
                event_labels[event_id] = str(event_label) # no unicode

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
        self.context.mapping_local_roles_context = {}

    def _initAreaContextRoles(self, node):
        mapping_areas = self.context.mapping_local_roles_context
        for child in node.childNodes:
            if child.nodeName != 'area':
                continue
            area_type = str(child.getAttribute('portal_type'))
            area = mapping_areas.setdefault(area_type, {})
            for subnode in child.childNodes:
                if subnode.nodeName != 'context-roles':
                    continue
                portal_type = str(subnode.getAttribute('portal_type'))
                role_labels = area.setdefault(portal_type, {})
                for e in subnode.childNodes:
                    if e.nodeName != 'role':
                        continue
                    role = str(e.getAttribute('id'))
                    role_label = self._getNodeText(e)
                    role_labels[role] = str(role_label) # no unicode

    def _extractDefaultEventMessages(self):
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

    def _purgeDefaultEventMessages(self):
        self.context.manage_editDefaultEventMessage(
            '', # err
            '', '', '', '', # sub
            '', '', '', '', # unsub
            event_default_email_title='',
            event_default_email_body='')

    def _initDefaultEventMessages(self, node):
        tool = self.context
        for child in node.childNodes:
            if child.nodeName != 'message':
                continue
            event_id, subject, body = self._getOneMessage(child)
            attrs = {
                '(default)': ('event_default_email_title',
                              'event_default_email_body'),
                '(error)': (None,
                            'event_error_email_body'),
                '(subscribe-confirm)': ('subscribe_confirm_email_title',
                                        'subscribe_confirm_email_body'),
                '(subscribed)': ('subscribe_welcome_email_title',
                                 'subscribe_welcome_email_body'),
                '(unsubscribe-confirm)': ('unsubscribe_confirm_email_title',
                                          'unsubscribe_confirm_email_body'),
                '(unsubscribed)': ('unsubscribe_email_title',
                                   'unsubscribe_email_body'),
                }.get(event_id)
            if attrs is None:
                continue
            subject_attr, body_attr = attrs
            if subject is not None and subject_attr is not None:
                setattr(tool, subject_attr, subject)
            if body is not None:
                setattr(tool, body_attr, body)

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

    def _getOneMessage(self, node):
        event_id = str(node.getAttribute('event_id'))
        subject, body = None, None
        for child in node.childNodes:
            if child.nodeName == 'subject':
                subject = self._getNodeText(child).encode('utf-8')
            elif child.nodeName == 'body':
                body = getExactNodeText(child).encode('utf-8')
        return event_id, subject, body

    def _purgeEventMessages(self):
        self.context.mapping_event_email_content = {}

    def _initEventMessages(self, node):
        # we could use manage_editEventMessage but the API is too dumb
        tool = self.context
        defaults = [tool.getDefaultMessageTitle(),
                    tool.getDefaultMessageBody()]
        event_messages = tool.mapping_event_email_content
        for child in node.childNodes:
            if child.nodeName != 'message':
                continue
            event_id, subject, body = self._getOneMessage(child)
            if event_id.startswith('('):
                continue
            messages = event_messages.setdefault(event_id, defaults[:])
            if subject is not None:
                messages[0] = subject
            if body is not None:
                messages[1] = body

    def createStrictTextElement(self, tagName):
        e = StrictTextElement(tagName)
        e.ownerDocument = self._doc
        return e

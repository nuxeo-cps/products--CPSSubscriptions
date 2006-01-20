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

        self._logger.info("Subscriptions tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeObjects()

        self._initProperties(node)
        self._initObjects(node)
        self._logger.info("Subscriptions tool imported.")


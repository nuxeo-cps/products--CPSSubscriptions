# Copyright (C) 2003 Nuxeo SARL <http://nuxeo.com>
# Copyright (C) 2003 CGEY <http://cgey.com>
# Copyright (c) 2003 Ministère de L'intérieur (MISILL)
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

from Globals import InitializeClass, DTMLFile, MessageDialog
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName

from zLOG import LOG, DEBUG, INFO

class Subscription(PortalFolder):
    """ Subscription

    Placefull Object containing subscription information.
    """

    meta_type = 'CPS Subscription Configuration'
    portal_type = meta_type

    security = ClassSecurityInfo()

    _properties = PortalFolder._properties + \
                  ({'id': 'filter_event_types', 'type': 'lines', 'mode': 'w',
                    'label': 'Filter Event Types'},
                   {'id': 'filter_object_types', 'type': 'lines', 'mode': 'w',
                    'label': 'Filter Object Types'},
                   )

    filter_event_types = []
    filter_object_types = []

    def __init__(self, id, title=''):
        """Constructor
        """
        PortalFolder.__init__(self, id, title)

        # The event types on which to react.
        self.filter_event_types = []

        # The types of the objects concerned by the subscription.
        self.filter_object_types = []

    def getFilterEventTypes(self):
        """ Returns the event types on which to react

        ex: workflow_create, workflow_in_publish
        """
        return self.filter_event_types

    def addEventType(self, event_type):
        """ Adds a new event type on wich to react

        ex: workflow_modify
        """
        if event_type not in getFilterEventTypes():
            self.filter_event_types += [event_type]

    def getFilterObjectTypes(self):
        """Returns the types of objects concerned by the subscription.

        The subscription is valid only if the
        context object's portal_type is in object_types.
        """
        return self.gilter_object_types

    def addObjectType(self, object_type):
        """Adds a new object type concerned with the subscription.

        """
        if object_type not in self.getFilterObjectTypes():
            self.filter_object_types += [object_type]

    def isInterestedInEvent(self, event_type, object, infos):
        """Is the subscription interested in the given event."""
        pass

    def sendEvent(self, event_type, object, infos):
        """Send an event to the subscription."""
        pass

    def getRecipientsRules(self):
        """Get the recipient rules objects.

        XXX matching what ?
        """
        # For tests.
        role_recipients_rule = 'role_recipients_role'
        return getattr(self, role_recipients_rule)

def addSubscription(self, id=None, REQUEST=None):
    """Add a Subscriptions object"""

    self = self.this()
    subtool = getToolByName(self, 'portal_subscriptions')
    id = subtool.getSubscriptionId()

    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = Subscription(id, title='Placefull Subscription')
    self._setObject(id, ob)

    LOG('addSubscriptions', INFO,
        'adding subscriptions %s/%s' % (self.absolute_url(), id))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

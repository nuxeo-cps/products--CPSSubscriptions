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

""" PlaceFull Subscription Folder Class
"""

from Globals import InitializeClass, DTMLFile, MessageDialog
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName

from Subscription import addSubscription

from zLOG import LOG, DEBUG, INFO

class PlaceFullSubscriptionFolder(PortalFolder):
    """ Subscription

    Placefull Object containing subscription information.
    """

    meta_type = 'CPS PlaceFull Subscription Folder'
    portal_type = meta_type

    security = ClassSecurityInfo()

    security.declarePublic("getSubscriptions")
    def getSubscriptions(self):
        """ Get all Subscriptions contained in here.
        """
        return [x for x in self.objectValues() if x.getFilterEventTypes]

InitializeClass(PlaceFullSubscriptionFolder)

def addPlaceFullSubscriptionFolder(self, id=None, REQUEST=None):
    """Add a Place Full Subscription Folder"""

    self = self.this()
    subtool = getToolByName(self, 'portal_subscriptions')
    id = subtool.getSubscriptionId()

    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = PlaceFullSubscriptionFolder(id, title='Placefull Subscription Folder')
    self._setObject(id, ob)

    subscription_folder = getattr(self, id)

    # Within skins to let the possiblity to users to customize it.
    event_types = self.getEventTypesFromContext()
    for event_type in event_types.keys():
        addSubscription(subscription_folder,
                        id='subscription__'+event_type,
                        title=event_types[event_type])

    LOG('addPlaceFullSubscriptionFolder', INFO,
        'adding subscriptions %s/%s' % (self.absolute_url(), id))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

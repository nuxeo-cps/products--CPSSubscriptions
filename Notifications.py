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

""" Notification rule classes

The something that is actually done.  Usually it involves Recipients (sending
email) but that's not mandatory (triggering an arbitrary script for instance).

Notifications are subclasses of NotificationRule and store also as
subobjects, like RecipientsRule.

"""

from Globals import InitializeClass, DTMLFile, MessageDialog
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName

from zLOG import LOG, DEBUG, INFO

class NotificationRule(PortalFolder):
    """Base Notification rule Class.

    All the Notifications will sub-class this one and implement a notification
    type.
    """

    def notifyRecipients(self, emails=[], members=[], **kw):
        """ Notify recipients

        This method will be called by the Subscription method.
        """
        raise NotImplementedError

InitializeClass(NotificationRule)

################################################################

class MailNotificationRule(NotificationRule):
    """Mail Notification

    Sending mail to the recipients of the subscription.
    """

    meta_type = "Mail Notification Rule"
    portal_type = meta_type

    def notifyRecipients(self, emails=[], members=[], **kw):
        """ Notify recipients

        This method will be called by the Subscription method.
        """
        raise NotImplementedError


InitializeClass(MailNotificationRule)

def addMailNotificationRule(self, id=None, title='', REQUEST=None, **kw):
    """Add a Mail Notification Rule object type
    """

    id = self.portal_subscriptions.getMailNotificationRuleObjectId()

    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = MailNotificationRule(id, title=title, **kw)
    self._setObject(id, ob)

    LOG('addRoleRecipientsRule', INFO,
        'adding recipients rule  %s/%s' % (self.absolute_url(), id))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Author : Julien Anguenot <ja@nuxeo.com>

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

"""Notification message body

Defines the NotificationMessageBody class. The aim of this class is define a
structure where to store the notification message bodies for further
scheduling

portal_subscriptions will store objects of this type.
"""

import time

from Globals import InitializeClass, DTMLFile
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent

addComputedRecipientsRuleForm = DTMLFile(
    'zmi/notification_message_body_addform',
    globals())

class NotificationMessageBody(PortalFolder):
    """Notification Message Body

    This class simply stores a mail body.
    """

    meta_type = 'NotificationMessageBody'
    portal_type = meta_type

    _properties = ({'id': 'message_body',
                    'type': 'text', 'mode':'w',
                    'label' : 'Message body'},
                   {'id': 'mime_type',
                    'type': 'string', 'mode':'w',
                    'label' : 'Mime Type'},)

    mime_type = 'text/plain'

    manage_options = PortalFolder.manage_options[2:4]

    security = ClassSecurityInfo()

    def __init__(self, id, title='',
                 message_body='',
                 mime_type='text/plain',
                 **kw):
        """Constructor

        Only take the message_body as a parameter
        """
        PortalFolder.__init__(self, id, title, **kw)
        self.message_body = message_body
        self.mime_type = mime_type

    security.declareProtected(ModifyPortalContent, 'updateMessageBody')
    def updateMessageBody(self, message_body=''):
        """Update the content of the message body
        """
        self.message_body = message_body

    security.declareProtected(View, 'getMessageBody')
    def getMessageBody(self):
        """Return the message body
        """
        return self.message_body

    security.declareProtected(View, 'getMimeType')
    def getMimeType(self):
        """Return the mime type of the message body
        """
        return self.mime_type

InitializeClass(NotificationMessageBody)

def addNotificationMessageBody(self,
                               id=None,
                               title='',
                               message_body='',
                               mime_type='text/plain',
                               REQUEST=None,
                               **kw):
    """Add a Notification Message body
    """

    # Use the BTreeFolder2 id generation facility
    # We are sure overlap is avoided
    if not id:
        id = aq_base(self).generateId(prefix='message_',
                                      suffix='',
                                      rand_ceiling=9999999999)

    ob = NotificationMessageBody(id,
                                 title=title,
                                 message_body=message_body,
                                 mime_type=mime_type,
                                 **kw)
    self._setObject(id, ob)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main')
    else:
        return id

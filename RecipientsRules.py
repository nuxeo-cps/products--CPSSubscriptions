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

""" Recipients Rules classes
"""

from Globals import InitializeClass, DTMLFile, MessageDialog
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName

from zLOG import LOG, DEBUG, INFO

class RecipientsRule(PortalFolder):
    """Recipients Rule Class.

    All the Recipients Rule types will sub-class this one.
    """

    def getRecipients(self, event_type, object, infos):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """
        pass

#######################################################

class ComputedRecipientsRule(RecipientsRule):
    """Computed Recipient Rules
    """

    meta_type = "Computed Recipients Rule"
    portal_type = meta_type

    security = ClassSecurityInfo()

    def getRecipients(self, event_type, object, infos):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """
        pass

InitializeClass(ComputedRecipientsRule)

def addComputedRecipientsRule(self, id=None, REQUEST=None):
    """ Add a computed recipients rule
    """
    self = self.this()
    id = 'computed_recipients_rule'
    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = ComputedRecipientsRule(id, title='Computed Recipients Rule')
    self._setObject(id, ob)

    LOG('addComputedRecipientsRule', INFO,
        'adding recipients rule  %s/%s' % (self.absolute_url(), id))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


########################################################

class ExplicitRecipientsRule(RecipientsRule):
    """Explicit Recipient Rules
    """
    meta_type = "Explicit Recipients Rules"
    portal_type = meta_type

    security = ClassSecurityInfo()

    def getRecipients(self, event_type, object, infos):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """
        pass

InitializeClass(ExplicitRecipientsRule)

def addExplicitRecipientsRule(self, id=None, REQUEST=None):
    """ Add an explicit recipients rule
    """
    self = self.this()
    id = 'explicit_recipients_rule'
    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = ExplicitRecipientsRule(id, title='Explicit Recipients Rule')
    self._setObject(id, ob)

    LOG('addExplicitRecipientsRule', INFO,
        'adding recipients rule  %s/%s' % (self.absolute_url(), id))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

#########################################################

class RoleRecipientsRule(RecipientsRule):
    """Role Recipient Rules
    """
    meta_type = "Role Recipient Rules"
    portal_type = meta_type

    security = ClassSecurityInfo()

    def getRecipients(self, event_type, object, infos):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """
        pass

InitializeClass(RoleRecipientsRule)

def addRoleRecipientsRule(self, id=None, REQUEST=None):
    """ Add a roles explicit Recipient rules
    """
    self = self.this()
    id = 'role_recipients_rule'
    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = RoleRecipientsRule(id, title='Explicit Recipients Rule')
    self._setObject(id, ob)

    LOG('addRoleRecipientsRule', INFO,
        'adding recipients rule  %s/%s' % (self.absolute_url(), id))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

#########################################################

class WorkflowImpliedRecipientsRule(RecipientsRule):
    """Workflow Implied Recipient Rule
    """
    meta_type = "Workflow Implied Recipient Rules"
    portal_type = meta_type

    security = ClassSecurityInfo()

    def getRecipients(self, event_type, object, infos):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """
        pass

InitializeClass(WorkflowImpliedRecipientsRule)

def addWorkflowImpliedRecipientsRule(self, id=None, REQUEST=None):
    """ Add a roles explicit Recipient rules
    """
    self = self.this()
    id = 'workflow_implied_recipients_rule'
    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = WorkflowImpliedRecipientsRule(id, title='Explicit Recipients Rule')
    self._setObject(id, ob)

    LOG('addWorkflowImpliedRecipientsRule', INFO,
        'adding recipients rule  %s/%s' % (self.absolute_url(), id))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

#############################################################

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
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent

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

InitializeClass(RecipientsRule)

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
        return {}

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
        return {}

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

    _properties = RecipientsRule._properties + \
                  ({'id': 'roles', 'type': 'lines', 'mode': 'w',
                    'label': 'Roles'},
                   {'id': 'origins', 'type': 'string', 'mode': 'r',
                    'label': 'Origins'},
                   {'id': 'ancestor_object_types', 'type': 'lines', 'mode': 'w',
                    'label': 'Ancestor Object Type'},
                   )

    roles = []
    origins = {}
    ancestor_object_types = []

    #
    # - roles -- The roles subscribed.
    # - origins -- A sequence describing how roles are looked up. It
    #   can contain the following keys:
    # - 'local': Direct local roles from the context object are
    #   used.
    # - 'merged': All merged local roles of the context object are
    #   used.
    # - 'ancestor_local': Direct local roles found on an ancestor
    #   object of type in ancestor_object_types. Only the closest
    #   matching ancestor object is used.
    # - 'ancestor_merged': Idem but with merged local roles.
    # - ancestor_object_types -- The portal types of the ancestor
    #   where a lookup of local roles is done if origins contains
    #  'ancestor_local' or 'ancestor_merged'.
    #

    def __init__(self, id, title='', **kw):
        """RoleRecipientsRule Constructor

        Call parent constructor and Init the properties
        """
        RecipientsRule.__init__(self, id, title)
        self.roles = kw.get('roles', [])
        self.origins = kw.get('origins', {})
        self.ancestor_object_types = kw.get('ancestor_object_types', [])

    security.declareProtected(View, 'getRoles')
    def getRoles(self):
        """ Returns the roles subscribed.
        """
        return self.roles

    security.declareProtected(ModifyPortalContent, 'addRole')
    def addRole(self, role):
        """ Add a new role
        """
        self.role += [role]

    def getRecipients(self, event_type, object, infos):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """
        member_email_mapping = {}
        mtool = self.portal_membership
        container = aq_parent(aq_inner(object))
        subtool = self.portal_subscriptions
        if getattr(self, 'notify_no_local'):
            if subtool.getSubscriptionId() in container.objectIds():
                return {}
        if not getattr(self, 'notify_local_only'):
            #
            # Using merged local roles
            #
            merged_local_roles = mtool.getMergedLocalRoles(container)
            for entry in merged_local_roles.keys():
                for role in self.getRoles():
                    if role in merged_local_roles[entry]:
                        if entry.startswith('user:'):
                            member_ids = [entry.split(':')[1]]
                        if entry.startswith('group:'):
                            group_id = entry.split(':')[1]
                            aclu = getattr(self, 'acl_users', None)
                            if group_id == 'role':
                                group_id = group_id + ':' + entry.split(':')[2]
                            group = aclu.getGroupById(group_id)
                            member_ids = group.getUsers()
                        for member_id in member_ids:
                            member = mtool.getMemberById(member_id)
                            if member is not None:
                                email = member.getProperty('email')
                                if email != '':
                                    member_email_mapping[email] = member_id
        else:
            #
            # Using roles defined only in the context
            #
            local_roles = container.get_local_roles()
            for member in local_roles:
                member_id = member[0]
                for role in self.getRoles():
                    if role in member[1]:
                        email = mtool.getMemberById(member_id).getProperty('email')
                        if email != '':
                            member_email_mapping[email] = member_id

            local_group_roles = container.get_local_group_roles()
            for group in local_group_roles:
                for role in self.getRoles():
                    if role in group[1]:
                        group_id = group[0]
                        aclu = getattr(self, 'acl_users', None)
                        group = aclu.getGroupById(group_id)
                        group_users = group.getUsers()
                        for member_id in group_users:
                            email = mtool.getMemberById(member_id).getProperty('email')
                            if email != '':
                                member_email_mapping[email] = member_id
        return member_email_mapping

InitializeClass(RoleRecipientsRule)

def addRoleRecipientsRule(self, id=None, title='', REQUEST=None, **kw):
    """ Add a roles explicit Recipient rules
    """
    if not id:
        id = self.computeId()
    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = RoleRecipientsRule(id, title=title, **kw)
    self._setObject(id, ob)

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
        return {}

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

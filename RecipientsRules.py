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

""" Recipients Rules classes

Classes defining how to compute recipients. They are stored within
the subscription container.
"""

from Globals import InitializeClass, MessageDialog
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from Products.CMFCore.PortalFolder import PortalFolder
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
        raise NotImplementedError

InitializeClass(RecipientsRule)

#######################################################

class ComputedRecipientsRule(RecipientsRule):
    """Computed Recipient Rules

    Several computed recipients rule can be stored within a subscription
    container.
    """

    meta_type = "Computed Recipients Rule"
    portal_type = meta_type

    security = ClassSecurityInfo()

    def getRecipients(self, event_type, object, infos):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """
        raise NotImplementedError

InitializeClass(ComputedRecipientsRule)

def addComputedRecipientsRule(self, id=None, REQUEST=None):
    """ Add a computed recipients rule
    """
    raise NotImplementedError

########################################################

class ExplicitRecipientsRule(RecipientsRule):
    """Explicit Recipient Rules Class

    Explicit member/groups/emails information.
    Only one explicit recipients rule object per subscription container.
    """

    #
    # For the moment the class provides these features :
    # -> Adding explicitly members
    # -> Adding explicitly groups
    # -> Adding explicitly emails
    #
    # This is the class that has to be completed to handle anonymous/members
    # subscribtions. <ja:15/01/2004>
    #

    meta_type = "Explicit Recipients Rule"
    portal_type = meta_type

    security = ClassSecurityInfo()

    _properties = RecipientsRule._properties + \
                  ({'id': 'members', 'type': 'lines', 'mode': 'w',
                    'label': 'Members subscribed manually'},
                   {'id': 'members_allow_add', 'type': 'lines', 'mode': 'w',
                    'label': 'Members Allow Add'},
                   {'id': 'groups', 'type': 'lines', 'mode': 'w',
                    'label': 'Groups subscribed manually'},
                   {'id': 'groups_allow_add', 'type': 'lines', 'mode': 'w',
                    'label': 'Groups Allow Add'},
                   {'id': 'emails', 'type': 'lines', 'mode': 'w',
                    'label': 'Emails subscribed Manually'},
                   {'id': 'emails_allow_add', 'type': 'lines', 'mode': 'w',
                    'label': 'Emails Allow Add'},
                   {'id': 'emails_confirm', 'type': 'lines', 'mode': 'w',
                    'label': 'Emails to be confirmed'},
                   {'id': 'emails_pending_add', 'type': 'lines', 'mode': 'w',
                    'label': 'Emails Pending Add'},
                   {'id': 'emails_pending_delete', 'type': 'lines', 'mode': 'w',
                    'label': 'Emails Pending Delete'},
                   )

    members = []
    members_allow_add = []
    groups = []
    groups_allow_add = []
    emails = []
    emails_allow_add = []
    emails_confirm = []
    emails_pending_add = []
    emails_pending_delete = []

    #
    # - members -- The ids of the members subscribed manually.
    #
    # - members_allow_add -- Whether members are allowed to
    #   subscribe / unsubscribe manually to the Subscription (adding
    #   themselves to recipient_members).
    #
    # - emails -- The emails subscribed manually.
    #
    # - emails_allow_add -- Whether anonymous visitors are allowed
    #   to subscribe / unsubscribe manually to the Subscription
    #   (adding themselves to recipient_emails).
    #
    # - emails_confirm -- Whether the emails have to be confirmed
    #   before being used. XXX this may be better as a global flag
    #   of portal_subcriptions instead..
    #
    # - emails_pending_add -- The emails subscribed manually but not
    #   yet confirmed.
    #
    # - emails_pending_delete -- The emails pending deletion from
    #   recipient_emails but not yet confirmed.
    #

    security.declarePublic("getMembers")
    def getMembers(self):
        """ Return all the member ids subscribed manually

        Returns a list of ids
        """
        return self.members

    security.declareProtected(ModifyPortalContent, "updateMembers")
    def updateMembers(self, member_ids=[]):
        """ Add explicitly member ids
        """
        for member_id in member_ids:
            if member_id not in self.members:
                self.members += [member_id]

    security.declarePublic("getGroups")
    def getGroups(self):
        """ Return all the group ids subscribed manually

        Returns a list of ids
        """
        return self.groups

    security.declareProtected(ModifyPortalContent, "updateGroups")
    def updateGroups(self, group_ids=[]):
        """ Add explicitly group ids
        """
        for group_id in group_ids:
            if group_id not in self.groups:
                self.groups += [group_id]

    security.declarePublic("getEmails")
    def getEmails(self):
        """ Return all the emails subscribed manually

        Returns a list of emails
        """
        return self.emails

    security.declareProtected(ModifyPortalContent, "updateEmails")
    def updateEmails(self, emails=[]):
        """ Add explicitly emails
        """
        self.emails = emails

    security.declareProtected(ModifyPortalContent, "getRecipients")
    def getRecipients(self, event_type, object, infos):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """

        member_email_mapping = {}
        mtool = self.portal_membership
        aclu = getattr(self, 'acl_users', None)

        #
        # Members subscribed manually
        #

        for member_id in self.getMembers():
            member = mtool.getMemberById(member_id)
            if member is not None:
                email = member.getProperty('email')
                member_email_mapping[email] = member_id

        #
        # Groups subscribed manually
        #

        for group_id in self.getGroups():
            group = aclu.getGroupById(group_id)
            group_users = group.getUsers()
            for member_id in group_users:
                member = mtool.getMemberById(member_id)
            if member is not None:
                email = member.getProperty('email')
                member_email_mapping[email] = member_id

        #
        # Standalone emails
        #

        for email in self.getEmails():
            member_email_mapping[email] = ''

        return member_email_mapping

InitializeClass(ExplicitRecipientsRule)

def addExplicitRecipientsRule(self, id=None, title='', REQUEST=None, **kw):
    """ Add an explicit recipients rule
    """

    id = self.portal_subscriptions.getExplicitRecipientsRuleId()

    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = ExplicitRecipientsRule(id, title='Explicit Recipients Rule', **kw)
    self._setObject(id, ob)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main')

#########################################################

class RoleRecipientsRule(RecipientsRule):
    """ Role Recipient Rules Class

    Roles based recipients rule computing.

    Several role recipients rule objects can exists within a subscription
    container
    """

    meta_type = "Role Recipient Rule"
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

    security.declareProtected(ModifyPortalContent, "getRecipients")
    def getRecipients(self, event_type, object, infos):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """
        member_email_mapping = {}
        mtool = self.portal_membership
        container = aq_parent(aq_inner(object))
        subtool = self.portal_subscriptions
        if getattr(self, 'notify_no_local'):
            if subtool.getSubscriptionContainerId() in container.objectIds():
                return {}
        if not getattr(self, 'notify_local_only'):
            #
            # Using merged local roles
            #
            merged_local_roles = mtool.getMergedLocalRoles(object)
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
            local_roles = object.get_local_roles()
            for member in local_roles:
                member_id = member[0]
                for role in self.getRoles():
                    if role in member[1]:
                        email = mtool.getMemberById(
                            member_id).getProperty('email')
                        if email != '':
                            member_email_mapping[email] = member_id

            local_group_roles = object.get_local_group_roles()
            for group in local_group_roles:
                for role in self.getRoles():
                    if role in group[1]:
                        group_id = group[0]
                        aclu = getattr(self, 'acl_users', None)
                        group = aclu.getGroupById(group_id)
                        group_users = group.getUsers()
                        for member_id in group_users:
                            email = mtool.getMemberById(member_id).getProperty(
                                'email')
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
        REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main')

#########################################################

class WorkflowImpliedRecipientsRule(RecipientsRule):
    """Workflow Implied Recipient Rule

    Several workflow implied recipients rule objects can be stored within a
    subscription container.
    """

    meta_type = "Workflow Implied Recipient Rule"
    portal_type = meta_type

    security = ClassSecurityInfo()

    def getRecipients(self, event_type, object, infos):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """
        raise NotImplementedError

InitializeClass(WorkflowImpliedRecipientsRule)

def addWorkflowImpliedRecipientsRule(self, id=None, REQUEST=None):
    """ Add a roles explicit Recipient rules
    """
    raise NotImplementedError

#############################################################

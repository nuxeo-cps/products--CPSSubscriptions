# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2004 CGEY <http://cgey.com>
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

from types import TupleType
from DateTime.DateTime import DateTime

from Globals import InitializeClass, MessageDialog, DTMLFile
from Acquisition import aq_base, aq_parent, aq_inner

from AccessControl import ClassSecurityInfo, getSecurityManager

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View

from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getEngine

from Products.CPSSubscriptions.permissions import CanSubscribe
from Products.CPSSubscriptions.permissions import ManageSubscriptions

from zLOG import LOG, ERROR

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

    Several computed recipients rules can be stored within a subscription
    container.

    It provides a tales expression that is supposed to return a dictionnary
    with email as key.
    """

    meta_type = "Computed Recipients Rule"
    portal_type = meta_type

    security = ClassSecurityInfo()

    _properties = (
        {'id' : 'expression',
         'type' : 'string',
         'mode' : 'w',
         'label' : 'TALES expression',
         },
        )

    expression = 'python:{}'
    expression_c = Expression(expression)

    _properties_post_process_tales = (
        ('expression', 'expression_c')
        )

    def __init__(self, id, title='', expr='python:{}'):
        """Init the expression attrs
        """
        PortalFolder.__init__(self, id, title=title)
        self.id = id
        self.expression = expr
        self.expression_c = Expression(self.expression)

    def getExpression(self, context, infos={}):
        """
        """
        try:
            self.expression_c = Expression(self.expression)
        except AttributeError:
            self.expression = 'python:{}'
        expr_context = self._createExpressionContext(context, infos)
        return self.expression_c(expr_context)

    def _createExpressionContext(self, context, infos={}):
        """Create an expression context for expression evaluation
        """
        mapping = {
            'portal': getToolByName(self, 'portal_url').getPortalObject(),
            'context': context,
            'proxy' : context,
            'doc': context.getContent(),
            'container': aq_parent(aq_inner(context)),
            'DateTime': DateTime,
            'Triggering_user': getSecurityManager().getUser(),
            'nothing': None,
            'infos': infos,
            }
        return getEngine().getContext(mapping)

    def getRecipients(self, event_type, object, infos={}):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """
        return self.getExpression(object, infos)

InitializeClass(ComputedRecipientsRule)

addComputedRecipientsRuleForm = DTMLFile(
    'zmi/computed_recipients_rules_addform',
    globals())

def addComputedRecipientsRule(self, id=None, title='',
                              expr='python:{}', REQUEST=None):
    """ Add a computed recipients rule
    """

    if not id:
        return MessageDialog(
            title='No id provided',
            message='You got to provide an id for this object',
            action='%s/manage_main' % REQUEST['URL1'])

    if id is not None:
        id = id + '__recipients_rule'

    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    if not title:
        title='Computed Recipients Rule'
    ob = ComputedRecipientsRule(id, title=title, expr=expr)
    self._setObject(id, ob)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main')

########################################################

class ExplicitRecipientsRule(RecipientsRule):
    """Explicit Recipient Rules Class

    Explicit member/groups/emails information. Only one explicit recipients
    rule object per subscription to store anoynmous / members explict
    subscriptions.

    Anoynmous may subscribe through a 2 step process. Requesting a subscription
    and then confirming it wheras the members can subscribe and unsubscribe
    freely
    """

    meta_type = "Explicit Recipients Rule"
    portal_type = meta_type

    security = ClassSecurityInfo()

    _properties = RecipientsRule._properties + \
                  ({'id': 'members', 'type': 'lines', 'mode': 'w',
                    'label': 'Members subscribed manually'},
                   {'id': 'members_allow_add', 'type': 'boolean', 'mode': 'w',
                    'label': 'Members Allow Add'},
                   {'id': 'groups', 'type': 'lines', 'mode': 'w',
                    'label': 'Groups subscribed manually'},
                   {'id': 'emails', 'type': 'lines', 'mode': 'w',
                    'label': 'Emails subscribed'},
                   {'id': 'emails_subscribers', 'type': 'lines', 'mode': 'w',
                    'label': 'Emails Subscribe Manually'},
                   {'id': 'emails_pending_add', 'type': 'lines', 'mode': 'w',
                    'label': 'Emails Pending Add'},
                   {'id': 'emails_pending_delete', 'type': 'lines', 'mode': 'w',
                    'label': 'Emails Pending Delete'},
                   )

    members = []
    members_allow_add = 0
    groups = []
    emails = []
    emails_subscribers = []
    emails_pending_add = []
    emails_pending_delete = []

    def __init__(self, id, title=''):
        """Init the expression attrs
        """
        PortalFolder.__init__(self, id, title=title)
        self.members = []
        self.members_allow_add = 0
        self.groups = []
        self.emails = []
        self.emails_subscribers = []
        self.emails_pending_add = []
        self.emails_pending_delete = []

    ######################################################
    ######################################################

    security.declarePublic("getMembers")
    def getMembers(self):
        """Return all the member subscribed manually

        Returns a list of ids
        """
        return self.members

    security.declarePublic("getMemberIds")
    def getMemberIds(self, context=None):
        """Return all the member Ids subscribed manually

        Returns a list of ids
        """
        if context is None:
            return [x['id'] for x in self.getMembers()]
        else:
            res = []
            for member_struct in self.getMembers():
                for url in member_struct['subscription_relative_url']:
                    if self._includesContextURL(context, url):
                        res.append(member_struct['id'])
                        continue
            return res

    security.declareProtected(ManageSubscriptions, "getMemberStrucById")
    def getMemberStructById(self, member_id):
        """Return the index of member_id in the list
        """
        for member_struct in self.members:
            if member_id == member_struct['id']:
                return member_struct
        return -1

    security.declareProtected(ManageSubscriptions, "updateMembers")
    def updateMembers(self, member_struct={}):
        """Add explicitly a member in a given context

        Notice a given member could have subscribed from different
        parts of the tree.

        XXX Don't store the absolute_url but the rpath instead...
        XXX refactore the namming of the member struct internal
        """
        self._p_changed = 1
        if member_struct:
            if member_struct.get('id') not in self.getMemberIds():
                self.members.append(member_struct)
            else:
                orig_struct = self.getMemberStructById(member_struct.get('id'))
                for candidate_url in member_struct.get(
                    'subscription_relative_url', ()):
                    if candidate_url not in orig_struct.get(
                        'subscription_relative_url'):
                        orig_struct.get('subscription_relative_url').append(
                            candidate_url)
            return 1
        return 0

    security.declareProtected(ManageSubscriptions, "removeMember")
    def removeMember(self, member_id, context_relative_url):
        """Remove the member defined by member_id in a given context.

        If not context anymore then we'll remove the user completely
        """
        self._p_changed = 1

        if member_id in self.getMemberIds():
            member_struct = self.getMemberStructById(member_id)
            urls = member_struct['subscription_relative_url']
            if context_relative_url in urls:
                new_urls = []
                for url in urls:
                    if url != context_relative_url:
                        new_urls.append(url)
                tmp_members = []
                for member in self.getMembers():
                    if member['id'] != member_id:
                        tmp_members.append(member)
                    else:
                        if new_urls:
                            member_struct[
                                'subscription_relative_url'] = new_urls
                            tmp_members.append(member_struct)
                self.members = tmp_members
                return 1
        return 0

    ######################################################
    ######################################################

    security.declarePublic("getGroups")
    def getGroups(self):
        """Return all the group ids subscribed manually

        Returns a list of ids
        """
        return self.groups

    security.declareProtected(ManageSubscriptions, "updateGroups")
    def updateGroups(self, group_ids=[]):
        """Add explicitly group ids
        """
        if not group_ids:
            return 0
        for group_id in group_ids:
            if group_id not in self.getGroups():
                self.groups += [group_id]
        return 1

    #####################################################
    #####################################################

    security.declarePublic("getEmails")
    def getEmails(self):
        """Return all the emails subscribed manually

        Returns a list of emails

        """
        return list(self.emails)

    security.declareProtected(ManageSubscriptions, "updateEmails")
    def updateEmails(self, emails=[]):
        """Add explicitly emails
        """
        self.emails = list(emails)

    #####################################################
    #####################################################

    security.declarePublic("getPendingEmails")
    def getPendingEmails(self):
        """Return all the emails subscribed manually

        Returns a list of emails
        """
        return list(self.emails_pending_add)

    security.declareProtected(ManageSubscriptions, "updatePendingEmails")
    def updatePendingEmails(self, email=''):
        """Add pending email subscription
        """
        self._p_changed = 1
        if (email and
            email not in self.getPendingEmails() and
            email not in self.getEmails()):
            # ZMI
            self.emails_pending_add = self.getPendingEmails()
            self.emails_pending_add.append(email)
            return 1
        return 0

    #####################################################
    #####################################################

    security.declarePublic("getPendingDeleteEmails")
    def getPendingDeleteEmails(self):
        """Return all the emails that are about to be deleted

        Returns a list of emails
        """
        return list(self.emails_pending_delete)

    security.declareProtected(ManageSubscriptions, 'updatePendingDeleteEmails')
    def updatePendingDeleteEmails(self, email=''):
        """Add pending delete email subscription
        """
        if (email and
            email not in self.getPendingDeleteEmails() and
            (email in self.getSubscriberEmails() or
             email in self.getEmails())):
            # ZMI
            self.emails_pending_delete = self.getPendingDeleteEmails()
            self.emails_pending_delete.append(email)
            return 1
        return 0

    ######################################################
    ######################################################

    security.declareProtected(ManageSubscriptions, 'getSubscriberEmails')
    def getSubscriberEmails(self):
        """Returns the anonymous subscriber emails

        return a list of emails
        """
        return list(self.emails_subscribers)

    security.declareProtected(ManageSubscriptions, 'updateSubscriberEmails')
    def updateSubscriberEmails(self, email=''):
        """Add email subscription (explicit)
        """
        if (email and
            email not in self.getSubscriberEmails()):
            self.emails_subscribers = self.getSubscriberEmails()
            self.emails_subscribers.append(email)
            return 1
        return 0

    security.declareProtected(ManageSubscriptions,
                              'importEmailsSubscriberList')
    def importEmailsSubscriberList(self, list=[]):
        """Add the list of emails to the subscriber list
        """
        self._p_changed = 1
        for email in list:
            self.updateSubscriberEmails(email)

    ######################################################
    ######################################################

    def _includesContextURL(self, context, url):
        """Does url includes the context URL
        """
        utool = getToolByName(self, 'portal_url')
        context_url = utool.getRelativeContentURL(context)
        return context_url.startswith(url) and 1

    ######################################################
    ######################################################

    security.declareProtected(CanSubscribe, 'subscribeTo')
    def subscribeTo(self, email, event_id, context):
        """Anonymous is asking for a subscription
        """
        self._p_changed = 1

        subtool = getToolByName(self, 'portal_subscriptions')
        notification_rule_id = subtool.getMailNotificationRuleObjectId()

        #
        # Getting notification rule object since he's the one sending
        # confirmation emails.
        # If this object is not in here then it means there's a problem
        #

        notification_rule = getattr(self, notification_rule_id, None)
        if notification_rule is None:
            LOG(" ::CPSSubscriptions:: subscribeTo()",
                ERROR,
                "Error : No mail notification found")
            return 0

        # Subscription information from the subscription container
        subscription_allowed = getattr(self, 'subscription_allowed')
        anonymous_allowed = getattr(self, 'anonymous_subscription_allowed')

        # Anonymous subscriptions
        if email:
            if not (subscription_allowed and anonymous_allowed):
                return 0
            if self.updatePendingEmails(email):
                notification_rule.notifyConfirmSubscription(event_id,
                                                           self,
                                                           email,
                                                           context)
                return 1

        # Member subscriptions.
        else:
            if not subscription_allowed:
                return 0
            membership_tool = getToolByName(self, 'portal_membership')
            member = membership_tool.getAuthenticatedMember()
            member_id = member.getMemberId()
            member_email = self.getMemberEmail(member_id) #skins

            # Building member struct with compuslory information
            utool = getToolByName(self, 'portal_url')
            context_relative_url = utool.getRelativeContentURL(context)

            member_struct = {}
            member_struct['id'] = member_id
            member_struct['subscription_relative_url'] = [context_relative_url]

            # Trying to subscribe the member
            if self.updateMembers(member_struct):
                notification_rule.notifyWelcomeSubscription(event_id,
                                                           self,
                                                           member_email,
                                                           context)
                # reindex the subscription  container for Zope-2.6.2
                subscription_container = getattr(context, '.cps_subscriptions')
                subscription_container.reindexObject()
                return 1
        return 0

    security.declareProtected(CanSubscribe, 'confirmSubscribeTo')
    def confirmSubscribeTo(self, email, event_id, context):
        """Anonymous confirm the subscription

        This method is in use only for anonymous since members
        are not requested to confirm after requesting a subscription

        We gonna check again if the anonymous is allowed to subscribe since
        it could have changed since the moment he requested the subscription
        """
        self._p_changed = 1

        subtool = getToolByName(self, 'portal_subscriptions')
        notification_rule_id = subtool.getMailNotificationRuleObjectId()

        #
        # Getting notification rule object since he's the one sending
        # confirmation emails.
        # If this object is not in here then it means there's a problem
        #

        notification_rule = getattr(self, notification_rule_id, None)
        if notification_rule is None:
            LOG(" ::CPSSubscriptions:: subscribeTo()",
                ERROR,
                "Error : No mail notification found")
            return 0

        # Subscription information from the subscription container
        subscription_allowed = getattr(self, 'subscription_allowed')
        anonymous_allowed = getattr(self, 'anonymous_subscription_allowed')

        # Anonymous subscriptions
        if not (subscription_allowed and anonymous_allowed):
            return 0

        if email in self.getPendingEmails():
            self.emails_subscribers.append(email)
            self.emails_pending_add.remove(email)
            notification_rule.notifyWelcomeSubscription(event_id,
                                                        self,
                                                        email,
                                                        context)
            return 1
        return 0

    #####################################################
    #####################################################

    security.declareProtected(CanSubscribe, 'unSubscribeTo')
    def unSubscribeTo(self, email, event_id, context):
        """Unsubscribe to a given event subscribption
        """
        self._p_changed = 1

        subtool = getToolByName(self, 'portal_subscriptions')
        notification_rule_id = subtool.getMailNotificationRuleObjectId()

        #
        # Getting notification rule object since he's the one sending
        # confirmation emails.
        # If this object is not in here then it means there's a problem
        #

        notification_rule = getattr(self, notification_rule_id, None)
        if notification_rule is None:
            LOG(" ::CPSSubscriptions:: subscribeTo()",
                ERROR,
                "Error : No mail notification found")
            return 0

        # Anonymous unsubscriptions
        if email:
            if self.updatePendingDeleteEmails(email):
                notification_rule.notifyConfirmUnSubscribe(event_id,
                                                           self,
                                                           email,
                                                           context)
                return 1

        # Member unsubscriptions.
        else:
            stupid_flag = 0

            membership_tool = getToolByName(self, 'portal_membership')
            member = membership_tool.getAuthenticatedMember()
            member_id = member.getMemberId()
            member_email = self.getMemberEmail(member_id) #skins

            if member_id in self.getMemberIds():
                # Building member struct with compuslory information
                utool = getToolByName(self, 'portal_url')
                context_relative_url = utool.getRelativeContentURL(context)
                self.removeMember(member_id, context_relative_url)
                stupid_flag = 1
            if stupid_flag:
                notification_rule.notifyUnSubscribe(event_id,
                                                    self,
                                                    member_email,
                                                    context)
                # reindex the subscription  container for Zope-2.6.2
                subscription_container = getattr(context, '.cps_subscriptions')
                subscription_container.reindexObject()
                return 1
        return 0

    security.declareProtected(CanSubscribe, 'confirmUnSubscribeTo')
    def confirmUnSubscribeTo(self, email, event_id, context):
        """Confirm unsubscribe to a given event subscription

        Only in use for anonymous.
        """
        self._p_changed = 1

        subtool = getToolByName(self, 'portal_subscriptions')
        notification_rule_id = subtool.getMailNotificationRuleObjectId()

        #
        # Getting notification rule object since he's the one sending
        # confirmation emails.
        # If this object is not in here then it means there's a problem
        #

        notification_rule = getattr(self, notification_rule_id, None)
        if notification_rule is None:
            LOG(" ::CPSSubscriptions:: subscribeTo()",
                ERROR,
                "Error : No mail notification found")
            return 0

        # Anonymous unsubscriptions
        if email:
            if email in self.getPendingDeleteEmails():
                self.emails_subscribers.remove(email)
                self.emails_pending_delete.remove(email)
                notification_rule.notifyUnSubscribe(event_id,
                                                   self,
                                                   email,
                                                   context)
                return 1
        return 0

    ###############################################################
    ###############################################################

    security.declareProtected(View, "getRecipients")
    def getRecipients(self, event_type, object, infos):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """

        member_email_mapping = {}
        mtool = self.portal_membership
        aclu = getattr(self, 'acl_users', None)

        #
        # It might not be an event nortification but just a request
        # in a given context such as the manager editing subscriptions
        # parameters. Thus we won't change the context since the context is
        # already given as a parameter (object)
        #

        subtool = getToolByName(self, 'portal_subscriptions')
        if object is None:
            pass
        elif object.portal_type not in subtool.getSubscribablePortalTypes():
            object = aq_parent(aq_inner(object))

        # Members subscribed
        for member_id in self.getMemberIds(context=object):
            email = self.getMemberEmail(member_id)
            member_email_mapping[email] = member_id

        # Groups subscribed
        for group_id in self.getGroups():
            try:
                group = aclu.getGroupById(group_id)
                group_users = group.getUsers()
                for member_id in group_users:
                    email = self.getMemberEmail(member_id)
                    member_email_mapping[email] = member_id
            except KeyError:
                # XXX
                pass

        # Explicit emails
        for email in self.getEmails():
            member_email_mapping[email] = ''

        # Anonymous subscribers emails
        for email in self.getSubscriberEmails():
            member_email_mapping[email] = ''

        return member_email_mapping

InitializeClass(ExplicitRecipientsRule)

def addExplicitRecipientsRule(self, id=None, title='', REQUEST=None, **kw):
    """Add an explicit recipients rule
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
    """Role Recipient Rules Class

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
                   {'id': 'unsubscribed_members', 'type': 'lines', 'mode': 'w',
                    'label': 'Unsubsribed members'},
                   )

    roles = []
    unsubscribed_members = []

    # XXX
    origins = {}
    ancestor_object_types = []

    def __init__(self, id, title='', **kw):
        """RoleRecipientsRule Constructor

        Call parent constructor and Init the properties
        """
        RecipientsRule.__init__(self, id, title)
        self.roles = kw.get('roles', [])
        self.origins = kw.get('origins', {})
        self.ancestor_object_types = kw.get('ancestor_object_types', [])
        self.unsubscribed_members = []

    security.declareProtected(View, 'getRoles')
    def getRoles(self):
        """Returns the roles subscribed.
        """

        return self.roles

    security.declareProtected(ManageSubscriptions, 'addRole')
    def addRole(self, role):
        """Add a new role
        """

        self.roles += [role]

    security.declarePublic('getUnSubscribedMembers')
    def getUnSubscribedMembers(self):
        """Returns the list of members who unsusbribed
        """

        return self.unsubscribed_members

    security.declareProtected(ManageSubscriptions, 'addUnSubscribedMember')
    def addUnSubscribedMember(self, member_id=''):
        """A member is unsubscribing
        """

        if member_id not in self.getUnSubscribedMembers():
            self.unsubscribed_members.append(member_id)

    security.declareProtected(View, "getRecipients")
    def getRecipients(self, event_type='', object=None, infos={}):
        """Get the recipients.

        Returns a mapping with 'members' and 'emails' as keys.
        """

        member_email_mapping = {}
        mtool = self.portal_membership
        subtool = self.portal_subscriptions
        if getattr(object, 'portal_type') in \
               subtool.getContainerPortalTypes():
            container = object
        else:
            container = aq_parent(aq_inner(object))

        if getattr(self, 'notify_no_local'):
            if subtool.getSubscriptionContainerId() in container.objectIds():
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
                                email = self.getMemberEmail(member_id)
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
                        email = self.getMemberEmail(member_id)
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
                            email = self.getMemberEmail(member_id)
                            member_email_mapping[email] = member_id


        #
        # Removing the members who asked for unsubsciption
        #

        for member_id in self.getUnSubscribedMembers():
            member_email = self.getMemberEmail(member_id)
            if member_email in member_email_mapping.keys():
                del member_email_mapping[member_email]

        return member_email_mapping

InitializeClass(RoleRecipientsRule)

def addRoleRecipientsRule(self, id=None, title='', REQUEST=None, **kw):
    """Add a roles explicit Recipient rules
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
    """Add a roles explicit Recipient rules
    """
    raise NotImplementedError

#############################################################

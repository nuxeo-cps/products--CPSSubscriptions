# $Id$

import os, sys
import unittest

import CPSSubscriptionsTestCase

from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem

from Products.CPSSubscriptions.RecipientsRules import RecipientsRule
from Products.CPSSubscriptions.RecipientsRules import ExplicitRecipientsRule
from Products.CPSSubscriptions.RecipientsRules import ComputedRecipientsRule
from Products.CPSSubscriptions.RecipientsRules import RoleRecipientsRule
from Products.CPSSubscriptions.RecipientsRules import \
     WorkflowImpliedRecipientsRule

# Some fake tools
class FakeTool(SimpleItem):
    pass

class FakeURLTool(Folder):
    def getPortalObject(self):
        # XXX dummy
        return self

class FakeContainer(Folder):
    portal_type = 'fake_container'
    def objectIds(self):
        return ('.cps_subscriptions',)


class TestBaseRecipientsRules(
    CPSSubscriptionsTestCase.CPSSubscriptionsTestCase):

    def afterSetUp(self):
        self.login('manager')
        self.portal.REQUEST.SESSION = {}
        self.portal.REQUEST.form = {}

    def beforeTearDown(self):
        self.logout()

class TestRecipientsRule(TestBaseRecipientsRules):

    def test_base(self):
        rr = RecipientsRule(id='fake')
        self.assertRaises(NotImplementedError, RecipientsRule.getRecipients,
                          rr, None, None, None)

class TestExplicitRecipientsRules(TestBaseRecipientsRules):

    def make_err(self):
        return ExplicitRecipientsRule('fake').__of__(self.portal)

    def test_fixtures(self):
        err = self.make_err()
        self.assertEqual(err.members, [])
        self.assertEqual(err.members_allow_add, 0)
        self.assertEqual(err.groups, [])
        self.assertEqual(err.emails, [])
        self.assertEqual(err.emails_subscribers, [])
        self.assertEqual(err.emails_pending_add , [])
        self.assertEqual(err.emails_pending_delete, [])

    def test_members(self):
        err = self.make_err()

        # Access to members prop and fixtures
        self.assertEqual(err.getMembers(), [])
        self.assertEqual(err.getMembers(), err.members)

        # API to access to internals
        self.assertEqual(err.getMemberIds(), [])

        # Get a struct
        self.assertEqual(err.getMemberStructById('fake_member_id'), -1)

        # Update Members
        example_struct = {'id' : 'manager',
                          'subscription_relative_url' :
                          [self.portal.absolute_url()],
                          }
        self.assert_(err.updateMembers(example_struct))

        # Test checkin
        self.assert_('manager' in err.getMemberIds())
        self.assertEqual(len(err.getMembers()), 1)

        # Get a non existent struct
        self.assert_(err.getMemberStructById('no_user'), -1)

        # Get the struct back
        checkout = err.getMemberStructById('manager')
        self.assert_(checkout)

        self.assertEqual(checkout.get('id'), 'manager')
        self.assertEqual(checkout.get('subscription_relative_url'),
                         [self.portal.absolute_url()])

        # Subscribe again with
        example_struct2 = {'id' : 'manager',
                          'subscription_relative_url' :
                           [self.portal.absolute_url() + '/sections',],
                          }
        self.assert_(err.updateMembers(example_struct2))

        # Test checkin
        self.assert_('manager' in err.getMemberIds())
        self.assertEqual(len(err.getMembers()), 1)

        # Get the struct back
        checkout = err.getMemberStructById('manager')
        self.assert_(checkout)

        self.assertEqual(checkout.get('id'), 'manager')
        self.assertEqual(checkout.get('subscription_relative_url'),
                         [self.portal.absolute_url(),
                          self.portal.absolute_url() + '/sections',
                          ])


        # Remove member from the /sections context
        err.removeMember('manager', self.portal.absolute_url() + '/sections')

        # Test checkin
        self.assert_('manager' in err.getMemberIds())
        self.assertEqual(len(err.getMembers()), 1)

        # Get a non existent struct
        self.assert_(err.getMemberStructById('no_user'), -1)

        # Get the struct back
        checkout = err.getMemberStructById('manager')
        self.assert_(checkout)

        self.assertEqual(checkout.get('id'), 'manager')
        self.assertEqual(checkout.get('subscription_relative_url'),
                         [self.portal.absolute_url()])


        # Final fixture
        err.removeMember('manager', self.portal.absolute_url())

        # Access to members prop and fixtures
        self.assertEqual(err.getMembers(), [])
        self.assertEqual(err.getMembers(), err.members)

        # API to access to internals
        self.assertEqual(err.getMemberIds(), [])

        # Chek manager subscription
        self.assertEqual(err.getMemberStructById('manager'), -1)

    def test_groups(self):
        err = self.make_err()

        self.assertEqual(err.groups, [])
        self.assertEqual(err.getGroups(), [])

        # ZMI behavior
        err.updateGroups(group_ids=('nuxeo1', 'nuxeo2'))
        self.assert_(err.getGroups())
        self.assertEqual(len(err.getGroups()), 2)
        self.assert_('nuxeo1' in err.getGroups())
        self.assert_('nuxeo2' in err.getGroups())

        # Try to add the same
        err.updateGroups(group_ids=('nuxeo1', 'nuxeo2'))
        self.assert_(err.getGroups())
        self.assertEqual(len(err.getGroups()), 2)
        self.assert_('nuxeo1' in err.getGroups())
        self.assert_('nuxeo2' in err.getGroups())

    def test_emails(self):
        err = self.make_err()

        self.assertEqual(err.emails, [])
        self.assertEqual(err.getEmails(), [])

        # ZMI behavior
        err.updateEmails(emails=('nuxeo@nuxeo.com',))
        self.assert_(err.getEmails())
        self.assertEqual(len(err.getEmails()), 1)
        self.assert_('nuxeo@nuxeo.com' in err.getEmails())

    def test_pending_add_emails(self):
        err = self.make_err()

        self.assertEqual(err.emails_pending_add, [])
        self.assertEqual(err.getPendingEmails(), [])

        # Add a pending emails
        self.assert_(err.updatePendingEmails('nuxeo@nuxeo.com'))
        self.assertEqual(len(err.getPendingEmails()), 1)
        self.assert_('nuxeo@nuxeo.com' in err.getPendingEmails())

        # Try to add the same one
        self.assert_(not err.updatePendingEmails('nuxeo@nuxeo.com'))

        # try to add a tuple
        # ZMI behavior
        err.emails_pending_add = ()

        # Add a pending emails
        self.assert_(err.updatePendingEmails('nuxeo@nuxeo.com'))
        self.assertEqual(len(err.getPendingEmails()), 1)
        self.assert_('nuxeo@nuxeo.com' in err.getPendingEmails())

        # Try to add the same one
        self.assert_(not err.updatePendingEmails('nuxeo@nuxeo.com'))

    def test_pending_del_emails(self):

        err = self.make_err()
        err = ExplicitRecipientsRule('fake')

        self.assertEqual(err.emails_pending_delete, [])
        self.assertEqual(err.getPendingDeleteEmails(), [])

        # Add the nuxeo@nuxeo.com email within the email subscribers
        # to test the API
        err.updateEmails(emails=('nuxeo@nuxeo.com',))
        self.assert_(err.getEmails())
        self.assertEqual(len(err.getEmails()), 1)
        self.assert_('nuxeo@nuxeo.com' in err.getEmails())

        # Add a pending delete email
        self.assert_(err.updatePendingDeleteEmails('nuxeo@nuxeo.com'))
        self.assertEqual(len(err.getPendingDeleteEmails()), 1)
        self.assert_('nuxeo@nuxeo.com' in err.getPendingDeleteEmails())

        # Try to delete the same one
        self.assert_(not err.updatePendingDeleteEmails('nuxeo@nuxeo.com'))

        # try to delete a tuple
        # ZMI behavior
        err.emails_pending_delete = ()

        # Delete a pending emails
        self.assert_(err.updatePendingDeleteEmails('nuxeo@nuxeo.com'))
        self.assertEqual(len(err.getPendingDeleteEmails()), 1)
        self.assert_('nuxeo@nuxeo.com' in err.getPendingDeleteEmails())

        # Try to add the same one
        self.assert_(not err.updatePendingDeleteEmails('nuxeo@nuxeo.com'))

    def test_subscribers_emails(self):

        err = self.make_err()
        err = ExplicitRecipientsRule('fake')

        self.assertEqual(err.emails_subscribers, [])
        self.assertEqual(err.getSubscriberEmails(), [])

        # add one
        self.assert_(err.updateSubscriberEmails('nuxeo@nuxeo.com'))
        self.assertEqual(len(err.getSubscriberEmails()), 1)
        self.assert_('nuxeo@nuxeo.com' in err.getSubscriberEmails())

        # Try to add the same
        self.assert_(not err.updateSubscriberEmails('nuxeo@nuxeo.com'))

        # try to delete a tuple
        # ZMI behavior
        err.emails_subscribers = ()

        self.assert_(err.updateSubscriberEmails('nuxeo@nuxeo.com'))
        self.assertEqual(len(err.getSubscriberEmails()), 1)
        self.assert_('nuxeo@nuxeo.com' in err.getSubscriberEmails())

        # Try to add the same
        self.assert_(not err.updateSubscriberEmails('nuxeo@nuxeo.com'))


    def test_group_is_gone(self):
        def getGroupById(id):
            raise KeyError, id

        class FakeSection:
            portal_type = 'Section'

        err = self.make_err()
        err = ExplicitRecipientsRule('fake')
        err.groups = ['GostGroup']
        self.portal._setObject('err', err)
        err = err.__of__(self.portal)

        self.portal.acl_users.getGroupById = getGroupById

        # this should not raise an error when aclu.getGroupById() returns None
        res = err.getRecipients('event_type', FakeSection(), 'infos')

        self.assertEquals(err.groups, [])


    def test_getRecipients(self):
        err = self.make_err()

        # Faking some required tools
        err.portal_membership = FakeTool()
        err.portal_subscriptions = FakeTool()

        # Nobody means no recipients
        self.assertEquals(err.getRecipients('fake_event', None, infos={}), {})

        # test with one member
        example_struct = {'id' : 'manager',
                          'subscription_relative_url' :
                          [self.portal.absolute_url()],
                          }
        self.assert_(err.updateMembers(example_struct))

        # that member has no email -> no recipient
        err.portal_membership.getEmailFromUsername = lambda _: None
        self.assertEquals(err.getRecipients('fake_event', None, infos={}), {})

        # that member has an email -> add it to the list
        err.portal_membership.getEmailFromUsername = {
            'manager': 'man@ager.net'}.get
        recipients = err.getRecipients('fake_event', None, infos={})
        self.assertEquals(recipients, {'man@ager.net': 'manager'})

        # test with a group of members
        class FakeGroup:
            def getUsers(self): return ('manager', 'toto')
        class FakeUserFolder:
            def getGroupById(self, _): return FakeGroup()
        err.acl_users = FakeUserFolder()
        err.updateGroups(group_ids=('some_group',))

        # toto has no email -> not a recipient
        recipients = err.getRecipients('fake_event', None, infos={})
        self.assertEquals(recipients, {'man@ager.net': 'manager'})

        # if toto has an email, it should be added to the recipients list
        err.portal_membership.getEmailFromUsername = {
            'manager': 'man@ager.net',
            'toto': 'toto@ager.net',
        }.get
        recipients = err.getRecipients('fake_event', None, infos={})
        self.assertEquals(recipients, {
            'man@ager.net': 'manager',
            'toto@ager.net': 'toto',
        })


    ##def test_subscription(self):
    ##    pass
    ##
    ##def test_unsubscription(self):
    ##    pass
    ##
    ##def test_confirm_subscribe(self):
    ##    pass
    ##
    ##def test_confirm_unsubscribe(self):
    ##    pass



class TestComputedRecipientsRules(TestBaseRecipientsRules):

    def test_fixtures(self):

        # Instanciation 1 : default expr
        err = ComputedRecipientsRule('fake', title='Fake')
        self.portal._setObject('err', err)
        err = self.portal['err']

        self.assertEqual(err.expression, 'python:{}')
        self.assertEqual(err.getRecipients('event_type', self.portal, {}), {})

        # Instanciation 2 : custom expression
        expr = "python:{'ja@nuxeo.com': 'Julien Anguenot'}"
        err2 = ComputedRecipientsRule('fake', title='Fake', expr=expr)
        self.portal._setObject('err2', err2)
        err2 = self.portal['err2']

        self.assertEqual(err2.expression, expr)
        self.assertEqual(err2.getRecipients('event_type', self.portal, {}),
                         {'ja@nuxeo.com': 'Julien Anguenot'})

class TestRoleRecipientsRules(TestBaseRecipientsRules):

    def test_fixtures(self):
        rrr = RoleRecipientsRule('fake')

    def test_getRecipients(self):
        rrr = RoleRecipientsRule('fake')

        # Faking some required tools
        rrr.portal_membership = FakeTool()
        rrr.portal_membership.getMergedLocalRoles = lambda _: {}

        rrr.portal_subscriptions = FakeTool()
        rrr.portal_subscriptions.getContainerPortalTypes = lambda: (
            'fake_container',)
        rrr.portal_subscriptions.getSubscriptionContainerId = lambda: (
            '.cps_subscriptions')

        # Faking a container object
        container = FakeContainer()

        # No role means no recipients whatever the configuration
        rrr.notify_no_local = True
        rrr.notify_local_only = False
        recipients = rrr.getRecipients('fake_event', container, infos={})
        self.assertEquals(recipients, {})

        rrr.notify_no_local = False
        recipients = rrr.getRecipients('fake_event', container, infos={})
        self.assertEquals(recipients, {})

        # test with one role
        rrr.addRole('FakeRole')
        self.assertEquals(rrr.getRoles(), ['FakeRole'])

        # Nobody has that role in that context
        recipients = rrr.getRecipients('fake_event', container, infos={})
        self.assertEquals(recipients, {})

        # manager has the role but no email
        # toto has a non matching role (and no email either)
        rrr.portal_membership.getMergedLocalRoles = lambda _: {
            'user:manager': ('FakeRole',),
            'user:toto': ('SomeOtherFakeRole',),
        }
        rrr.portal_membership.getEmailFromUsername = lambda _: None
        recipients = rrr.getRecipients('fake_event', container, infos={})
        self.assertEquals(recipients, {})

        # manager has an email -> add it to the list
        # toto has an email too but not the matching role -> not the list
        rrr.portal_membership.getEmailFromUsername = {
            'manager': 'man@ager.net',
            'toto': 'toto@ager.net',
        }.get

        recipients = rrr.getRecipients('fake_event', container, infos={})
        self.assertEquals(recipients, {'man@ager.net': 'manager'})

        # test with a group of members
        class FakeGroup:
            def getUsers(self): return ('manager', 'toto', 'toto_no_email')
        class FakeUserFolder:
            def getGroupById(self, id):
                return {'some_group': FakeGroup()}[id] # KeyError is wanted
        rrr.acl_users = FakeUserFolder()
        rrr.portal_membership.getMergedLocalRoles = lambda _: {
            'user:manager': ('FakeRole',),
            'group:some_group': ('FakeRole',),
            'group:some_other_group': ('SomeOtherFakeRole',),
        }
        recipients = rrr.getRecipients('fake_event', container, infos={})
        self.assertEquals(recipients, {
            'man@ager.net': 'manager',
            'toto@ager.net': 'toto',
        })

        # test with a group that does not exist (#1955) having the relevant role
        rrr.portal_membership.getMergedLocalRoles = lambda _: {
            'user:manager': ('FakeRole',),
            'group:some_other_group': ('FakeRole',),
            'group:some_group': ('FakeRole',),
        }
        recipients = rrr.getRecipients('fake_event', container, infos={})
        self.assertEquals(recipients, {
            'man@ager.net': 'manager',
            'toto@ager.net': 'toto',
        })

        # Same setting but only some local roles are taken into accounts:
        container.get_local_roles = lambda: (
            ('manager', ('FakeRole',)),
            ('toto', ('SomeOtherFakeRole',)),
            ('toto_no_email', ('FakeRole',)),
        )
        container.get_local_group_roles = lambda: ()
        rrr.notify_local_only = True
        recipients = rrr.getRecipients('fake_event', container, infos={})
        self.assertEquals(recipients, {'man@ager.net': 'manager'})

        # adding some more groups with no merged local roles
        container.get_local_group_roles = lambda: (
            ('some_group', ('FakeRole',)),)
        recipients = rrr.getRecipients('fake_event', container, infos={})
        self.assertEquals(recipients, {
            'man@ager.net': 'manager',
            'toto@ager.net': 'toto',
        })

        # again for #1955
        container.get_local_group_roles = lambda: (
            ('unknown_group', ('FakeRole',)),
            ('some_group', ('FakeRole',)),)
        recipients = rrr.getRecipients('fake_event', container, infos={})
        self.assertEquals(recipients, {
            'man@ager.net': 'manager',
            'toto@ager.net': 'toto',
        })

        # Checking with notify_no_local
        rrr.notify_no_local = True
        recipients = rrr.getRecipients('fake_event', container, infos={})
        self.assertEquals(recipients, {})

    def test_getRecipients_no_expand(self):
        # preparing the groups directory etc.
        sch = self.portal.portal_schemas['groups']
        sch.addField('email', 'CPS String Field')
        gdir = self.portal.portal_directories['groups']
        gdir._createEntry({'group': 'some_group',
                           'members': ('manager',),
                           'email': 'some_group@lists.example.net'})
        self.portal.acl_users.groups_email_field = 'email'

        # Faking a container object
        container = FakeContainer().__of__(self.portal)
        rrr = RoleRecipientsRule('fake').__of__(container)

        # Faking some required tools
        rrr.portal_membership = FakeTool()
        rrr.portal_membership.getMergedLocalRoles = lambda _: {}

        rrr.portal_subscriptions = FakeTool().__of__(self.portal)
        rrr.portal_subscriptions.getContainerPortalTypes = lambda: (
            'fake_container',)
        rrr.portal_subscriptions.getSubscriptionContainerId = lambda: (
            '.cps_subscriptions')

        # No role means no recipients whatever the configuration
        rrr.notify_no_local = True
        rrr.notify_local_only = False
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)

        void = ({}, {})
        self.assertEquals(recipients, void)

        rrr.notify_no_local = False
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)

        self.assertEquals(recipients, void)

        # test with one role
        rrr.addRole('FakeRole')
        self.assertEquals(rrr.getRoles(), ['FakeRole'])

        # Nobody has that role in that context
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)

        self.assertEquals(recipients, void)

        rrr.portal_membership.getEmailFromUsername = {
            'manager': 'man@ager.net',
        }.get


        # role:authenticated
        rrr.acl_users.email_for_authenticated = 'all@cps.example'

        rrr.portal_membership.getMergedLocalRoles = lambda _: {
            'group:role:Authenticated': ('FakeRole',),
        }
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)
        self.assertEquals(recipients,
                          ({}, {'all@cps.example': 'role:Authenticated'}))

        # Again with no address specified
        rrr.acl_users.email_for_authenticated = ''
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)
        self.assertEquals(recipients, ({}, {}))

        # Just the user
        rrr.portal_membership.getMergedLocalRoles = lambda _: {
            'user:manager': ('FakeRole',),
            'group:some_group': ('SomeOtherFakeRole',),
            'group:some_other_group': ('SomeOtherFakeRole',),
        }
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)
        self.assertEquals(recipients, ({'man@ager.net': 'manager',}, {}))

        # The user and the group
        rrr.portal_membership.getMergedLocalRoles = lambda _: {
            'user:manager': ('FakeRole',),
            'group:some_group': ('FakeRole',),
        }
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)
        self.assertEquals(recipients, (
            {'man@ager.net': 'manager',},
            {'some_group@lists.example.net' : 'some_group'},))

        # Just the group
        rrr.portal_membership.getMergedLocalRoles = lambda _: {
            'user:manager': ('SomeOtherFakeRole',),
            'group:some_group': ('FakeRole',),
        }
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)
        self.assertEquals(recipients, (
            {},
            {'some_group@lists.example.net' : 'some_group',}))

        # test with a group that does not exist (#1955) having the relevant role
        rrr.portal_membership.getMergedLocalRoles = lambda _: {
            'user:manager': ('FakeRole',),
            'group:some_other_group': ('FakeRole',),
            'group:some_group': ('FakeRole',),
        }
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)
        self.assertEquals(recipients, (
            {'man@ager.net': 'manager',},
            {'some_group@lists.example.net' : 'some_group'},))

        # Same setting but only some local roles are taken into accounts:
        container.get_local_roles = lambda: (
            ('manager', ('FakeRole',)),
            ('toto', ('SomeOtherFakeRole',)),
            ('toto_no_email', ('FakeRole',)),
        )
        container.get_local_group_roles = lambda: ()
        rrr.notify_local_only = True
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)

        self.assertEquals(recipients, ({'man@ager.net': 'manager'}, {}))

        # adding some more groups with no merged local roles
        container.get_local_group_roles = lambda: (
            ('some_group', ('FakeRole',)),)
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)
        self.assertEquals(recipients, (
            {'man@ager.net': 'manager',},
            {'some_group@lists.example.net' : 'some_group'},))

        # again for #1955
        container.get_local_group_roles = lambda: (
            ('unknown_group', ('FakeRole',)),
            ('some_group', ('FakeRole',)),)
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)
        self.assertEquals(recipients, (
            {'man@ager.net': 'manager',},
            {'some_group@lists.example.net' : 'some_group'},))

        # Checking with notify_no_local
        rrr.notify_no_local = True
        recipients = rrr.getRecipients('fake_event', container, infos={},
                                       expand_groups=False)

        self.assertEquals(recipients, void)


class TestWorkflowImpliedRecipientsRules(TestBaseRecipientsRules):

    def test_fixtures(self):
        wrr = WorkflowImpliedRecipientsRule('fake')

    # XXX

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRecipientsRule))
    suite.addTest(unittest.makeSuite(TestExplicitRecipientsRules))
    suite.addTest(unittest.makeSuite(TestComputedRecipientsRules))
    suite.addTest(unittest.makeSuite(TestRoleRecipientsRules))
    suite.addTest(unittest.makeSuite(TestWorkflowImpliedRecipientsRules))
    return suite

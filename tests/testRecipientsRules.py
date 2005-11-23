# $Id$

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest

import CPSSubscriptionsTestCase

from OFS.Folder import Folder

from Products.CPSSubscriptions.RecipientsRules import RecipientsRule
from Products.CPSSubscriptions.RecipientsRules import ExplicitRecipientsRule
from Products.CPSSubscriptions.RecipientsRules import ComputedRecipientsRule
from Products.CPSSubscriptions.RecipientsRules import RoleRecipientsRule
from Products.CPSSubscriptions.RecipientsRules import \
     WorkflowImpliedRecipientsRule

class FakeURLTool(Folder):
    def getPortalObject(self):
        # XXX dummy
        return self

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

    def test_fixtures(self):

        err = ExplicitRecipientsRule('fake')
        self.assertEqual(err.members, [])
        self.assertEqual(err.members_allow_add, 0)
        self.assertEqual(err.groups, [])
        self.assertEqual(err.emails, [])
        self.assertEqual(err.emails_subscribers, [])
        self.assertEqual(err.emails_pending_add , [])
        self.assertEqual(err.emails_pending_delete, [])

    def test_members(self):
        err = ExplicitRecipientsRule('fake')

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

        err = ExplicitRecipientsRule('fake')
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

        err = ExplicitRecipientsRule('fake')
        self.assertEqual(err.emails, [])
        self.assertEqual(err.getEmails(), [])

        # ZMI behavior
        err.updateEmails(emails=('nuxeo@nuxeo.com',))
        self.assert_(err.getEmails())
        self.assertEqual(len(err.getEmails()), 1)
        self.assert_('nuxeo@nuxeo.com' in err.getEmails())

    def test_pending_add_emails(self):

        err = ExplicitRecipientsRule('fake')
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

        err = ExplicitRecipientsRule('fake')
        err.groups = ['GostGroup']
        self.portal._setObject('err', err)
        err = err.__of__(self.portal)

        self.portal.acl_users.getGroupById = getGroupById

        # this should not raise an error when aclu.getGroupById() returns None
        res = err.getRecipients('event_type', FakeSection(), 'infos')

        self.assertEquals(err.groups, [])


    ##def test_getRecipients(self):
    ##    pass
    ##
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
        err = RoleRecipientsRule('fake')

    # XXX

class TestWorkflowImpliedRecipientsRules(TestBaseRecipientsRules):

    def test_fixtures(self):
        err = WorkflowImpliedRecipientsRule('fake')

    # XXX

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRecipientsRule))
    suite.addTest(unittest.makeSuite(TestExplicitRecipientsRules))
    suite.addTest(unittest.makeSuite(TestComputedRecipientsRules))
    suite.addTest(unittest.makeSuite(TestRoleRecipientsRules))
    suite.addTest(unittest.makeSuite(TestWorkflowImpliedRecipientsRules))
    return suite

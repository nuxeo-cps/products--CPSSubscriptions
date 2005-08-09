# -*- coding: iso-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Julien Anguenot <ja@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
"""Tests for the Indexation Manager
"""

import random
import unittest
from OFS.SimpleItem import SimpleItem

from Products.CPSSubscriptions.EventManager import EventManager
from Products.CPSSubscriptions.EventManager import get_event_manager

try:
    import transaction
except ImportError: # BBB: for Zope 2.7
    from Products.CMFCore.utils import transaction

class DummySubscriptionsTool:

    def __init__(self):
        self.id = 'portal_subscriptions'
        self.log = []

    def getLog(self):
        log = self.log
        self.log = []
        return log

    def notify_processed_event(self, event_type, object, infos):
        self.log.append("event_type : %s, object : %s , infos : %s"
                        %(event_type, str(object.id), str(infos)))

portal_subscriptions = DummySubscriptionsTool()

class FakeTransaction:
    def beforeCommitHookOrdered(self, hook, order):
        pass

class FakeRoot:

    __objects__ = {}

    def generateId(self):
        id = random.randrange(1000000)
        while id in self.__objects__.keys():
            id = random.randrange(1000000)
        return id

    def unrestrictedTraverse(self, path, default):
        dummy, id = path
        assert dummy == ''
        return self.getDummy(int(id))

    def addDummy(self, cls=None):
        id = self.generateId()
        if cls is None:
            cls = Dummy
        ob = cls(id)
        self.__objects__[id] = ob
        return ob

    def getDummy(self, id):
        return self.__objects__.get(id)

    def clear(self):
        self.__objects__ = {}

root = FakeRoot()

class Dummy:

    def __init__(self, id):
        self.id = id
        self.log = []
        self.portal_subscriptions = portal_subscriptions

    def getLog(self):
        # get and clear log
        log = self.log
        self.log = []
        return log

    def getPhysicalRoot(self):
        return root

    def getPhysicalPath(self):
        return ('', str(self.id))

class EventManagerTest(unittest.TestCase):

    def get_manager(self):
        return EventManager(FakeTransaction())

    def test_compute_key(self):

        mgr = self.get_manager()
        dummy = root.addDummy()
        self.assertEqual(mgr._computeKeyFor(dummy, 'event_id'),
                         ('event_id', (id(dummy), str(dummy.id))))

    def test_push_events(self):

        mgr = self.get_manager()

        # Push one
        dummy1 = Dummy('dummy1')
        mgr.push('event_id', dummy1, {})
        self.assertEqual(len(mgr._events.keys()), 1)

        # Push another one
        dummy2 = Dummy('dummy2')
        mgr.push('event_id', dummy2, {})
        self.assertEqual(len(mgr._events.keys()), 2)

        # Push the first one again with the same event
        mgr.push('event_id', dummy1, {})
        self.assertEqual(len(mgr._events.keys()), 2)

        # Push the seconf one again with the same event
        mgr.push('event_id', dummy2, {})
        self.assertEqual(len(mgr._events.keys()), 2)

        # Push the first one with another event
        mgr.push('other_event_id', dummy1, {})
        self.assertEqual(len(mgr._events.keys()), 3)

        # Push the second one with another event
        mgr.push('other_event_id', dummy2, {})
        self.assertEqual(len(mgr._events.keys()), 4)

    def test_manager_call(self):

        mgr = self.get_manager()

        dummy = root.addDummy()
        mgr.push('event_id', dummy, {})

        mgr()
        self.assert_(
            dummy.portal_subscriptions.getLog(),
            ['event_type : event_id, object : %s , infos : {}' %dummy.id
             ])

        root.clear()

    def test_synchronous(self):
        mgr = self.get_manager()
    
        dummy = root.addDummy()
        self.assertEquals(dummy.portal_subscriptions.getLog(), [])
    
        mgr.push('event_id', dummy, {})
        self.assertEquals(dummy.portal_subscriptions.getLog(), [])
    
        mgr.setSynchonous(True)
        self.assertEquals(
            dummy.portal_subscriptions.getLog(),
            ["event_type : event_id, object : %s , infos : {}" %dummy.id])
    
        mgr.setSynchonous(False)
        mgr.push('event_id', dummy, {'c':'c'})
        self.assertEquals(dummy.getLog(), [])
    
        mgr()
        self.assertEquals(
            dummy.portal_subscriptions.getLog(),
            ["event_type : event_id, object : %s , infos : {'c': 'c'}"%dummy.id])
        root.clear()

class TransactionEventManagerTest(unittest.TestCase):

    # These really test the beforeCommitHook

    def test_transaction(self):
        transaction.begin()
        mgr = get_event_manager()
        dummy = root.addDummy()
        mgr.push('event_id', dummy, {})
        self.assertEquals(dummy.portal_subscriptions.getLog(), [])
        transaction.commit()
        self.assertEquals(
            dummy.portal_subscriptions.getLog(),
            ["event_type : event_id, object : %s , infos : {}" %dummy.id])
        root.clear()

    def test_transaction_aborting(self):
        transaction.begin()
        mgr = get_event_manager()
        dummy = root.addDummy()
        mgr.push('event_id', dummy, {})
        self.assertEquals(dummy.portal_subscriptions.getLog(), [])
        transaction.abort()
        self.assertEquals(dummy.portal_subscriptions.getLog(), [])
        root.clear()
        
    
    def test_transaction_nested(self):
        transaction.begin()
        mgr = get_event_manager()
        dummy = root.addDummy()
        other = root.addDummy()
        dummy.other = other

        mgr.push('event_id', dummy, {})
        mgr.push('event_id', other, {})
        
        self.assertEquals(dummy.portal_subscriptions.getLog(), [])
        transaction.commit()
        logs = dummy.portal_subscriptions.getLog()
        for eid in (other.id, dummy.id):
            self.assert_(
                "event_type : event_id, object : %s , infos : {}" %eid in logs)
        root.clear()

from Products.CPSCore.ProxyBase import ProxyFolderishDocument
from Products.CPSCore.ProxyBase import ProxyBTreeFolderishDocument

class FolderishDummy(Dummy, ProxyFolderishDocument):
    pass

class BTreeFolderishDummy(Dummy, ProxyBTreeFolderishDocument):
    pass

class EventManagerSpecificsTest(unittest.TestCase):

    # Test Event Manager Specifics

    def test_folderish(self):

        dummy = root.addDummy(cls=FolderishDummy)
        other = root.addDummy()
        dummy.other = other

        mgr = get_event_manager()
        mgr.push('event_id', dummy, {})
        mgr.push('event_id', other, {})

        mgr()

        self.assert_(len(dummy.portal_subscriptions.getLog()), 1)

    def test_btree_folderish_simple(self):

        dummy = root.addDummy(cls=BTreeFolderishDummy)
        other = root.addDummy()
        dummy.other = other

        mgr = get_event_manager()
        mgr.push('event_id', dummy, {})
        mgr.push('event_id', other, {})

        mgr()

        self.assert_(len(dummy.portal_subscriptions.getLog()), 1)

    def test_btree_folderish_simple(self):

        dummy = root.addDummy(cls=BTreeFolderishDummy)
        other = root.addDummy()
        dummy.other = other
        another = root.addDummy()

        mgr = get_event_manager()
        mgr.push('event_id', dummy, {})
        mgr.push('event_id', other, {})
        mgr.push('event_id', another, {})

        mgr()

        self.assert_(len(dummy.portal_subscriptions.getLog()), 2)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(EventManagerTest),
        unittest.makeSuite(TransactionEventManagerTest),
        unittest.makeSuite(EventManagerSpecificsTest),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())

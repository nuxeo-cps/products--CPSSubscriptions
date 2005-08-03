# -*- coding: iso-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors: Julien Anguenot <ja@nuxeo.com>
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
"""Manager for event that can be that can be delayed until commit
time.

Asynchronous by default.
"""

from zLOG import LOG, DEBUG
from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

try:
    import transaction
except ImportError:
    # BBB: for Zope 2.7
    from Products.CMFCore.utils import transaction
    # The following is missing from CMF 1.5.2
    def BBBget():
        return get_transaction()
    transaction.get = BBBget


_TXN_MGR_ATTRIBUTE = '_cps_event_manager'

class EventManager:
    """Holds events that need to be processed."""

    # Not synchronous by default
    # XXX This may be monkey-patched by unit-tests.
    DEFAULT_SYNC = False

    def __init__(self, txn):
        """Initialize and register this manager with the transaction."""
        self._events = {}
        self._sync = self.DEFAULT_SYNC
        txn.beforeCommitHook(self)

    def setSynchonous(self, sync):
        """Set queuing mode."""
        if sync:
            self()
        self._sync = sync

    def isSynchonous(self):
        """Get queuing mode."""
        return self._sync

    def push(self, event_type, object, info):
        """Push the event in a queue
        """
        rpath = '/'.join(object.getPhysicalPath())[1:]

        i = (id(aq_base(object)), rpath)
        eid = (event_type, i)

        event_info = {'id' : i,
                      'object': object,
                      }

        cinfo = self._events.get(eid)
        if cinfo is None:
            self._events[eid] = (event_info, info)
        else:
            # XXX probably not what's needed here.
            self._events[eid][0].update(event_info)
            self._events[eid][1].update(info)

    def __call__(self):
        """Called when transaction commits.

        Dispatch the events to the susbcriptions tool todo the actual
        processing
        """
        LOG("EventManager", DEBUG, "__call__")
        for k, v in self._events.items():
            ob = v[0]['object']
            root = ob.getPhysicalRoot()
            path = ob.getPhysicalPath()
            old_ob = ob
            ob = root.unrestrictedTraverse(path, None)
            if ob is None:
                LOG("EventManager", DEBUG, "Object %r disappeard"%old_ob)
            else:
                subtool = getToolByName(ob, 'portal_subscriptions')
                if subtool is not None:
                    LOG("EventManager", DEBUG, "Processing event for %r "%(ob))
                    subtool.notify_processed_event(k[0], ob, v[1])
                else:
                    LOG("EventManager", DEBUG, "Subscriptions Tool not found")
        LOG("EventManager", DEBUG, "__call__ DONE")

def _remove_event_manager():
    txn = transaction.get()
    setattr(txn, _TXN_MGR_ATTRIBUTE, None)

def get_event_manager():
    """Get the event manager.

    Creates it if needed.
    """
    txn = transaction.get()
    mgr = getattr(txn, _TXN_MGR_ATTRIBUTE, None)
    if mgr is None:
        mgr = EventManager(txn)
        setattr(txn, _TXN_MGR_ATTRIBUTE, mgr)
    return mgr

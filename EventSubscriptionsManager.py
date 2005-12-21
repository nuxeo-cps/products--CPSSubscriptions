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
"""Manager for event subscriptions with a delayed processing until commit time.

Asynchronous by default.
"""

import logging
import transaction
import zope.interface

from Acquisition import aq_base, aq_inner, aq_parent

from Products.CMFCore.utils import getToolByName

from Products.CPSCore.interfaces import IBaseManager
from Products.CPSCore.BaseManager import BaseManager
from Products.CPSCore.TransactionManager import (
    get_before_commit_subscribers_manager
    )

from Products.CPSCore.ProxyBase import ProxyFolderishDocument
from Products.CPSCore.ProxyBase import ProxyBTreeFolderishDocument

_EVT_MGR_ATTRIBUTE = '_cps_event_subscriptions_manager'
_EVT_MGR_ORDER = 100

class EventSubscriptionsManager(BaseManager):
    """Holds subscription events that need to be processed."""

    zope.interface.implements(IBaseManager)

    def __init__(self, mgr):
        """Initialize and register this manager with the transaction.
        """
        BaseManager.__init__(self, mgr, order=_EVT_MGR_ORDER)
        self._events = {}
        self.log = logging.getLogger(
            "CPSSubscriptions.EventSubscriptionsManager")

    def _computeKeyFor(self, object, event_type):
        """Compute the key for the queue element
        """
        rpath = '/'.join(object.getPhysicalPath())[1:]
        i = (id(aq_base(object)), rpath)
        return (event_type, i)

    def _isObjectInteresting(self, object):
        """Filter the objects we don't want to cope with

        Add filter in here if necessarly.
        """
        repo = getToolByName(object, 'portal_repository', None)
        # Events outside CPS. We don't deal with those.
        if repo is not None:
            return not repo.isObjectInRepository(object)
        return False

    def push(self, event_type, object, info):
        """Push the event in a queue with the related info.
        """

        # Do not push anything if the subscriber is not enabled
        # When the manager is disabled it won't queue anything. It means, it
        # can be deactiveted for a while, thus won't queue, and then be
        # activated again and start queuing again.
        if not self._status:
            self.log.debug("is DISABELED. "
                           "Will *not* process event %s for %r with infos %r"
                           %(event_type, object, info))
            return

        if not self._isObjectInteresting(object):
            return

        eid = self._computeKeyFor(object, event_type)

        event_info = {'id' : eid[1],
                      'object': object,
                      }

        self.log.debug("push for %s: %r"%(event_type, event_info))

        cinfo = self._events.get(eid)
        if cinfo is None:
            self._events[eid] = (event_info, info)
        else:
            self._events[eid][0].update(event_info)
            self._events[eid][1].update(info)

    def __call__(self):
        """Called when transaction commits.

        Dispatch the events to the susbcriptions tool todo the actual
        processing
        """

        # XXX this code should move to an external callable

        self.log.debug("__call__")
        for k, v in self._events.items():
            ob = v[0]['object']
            root = ob.getPhysicalRoot()
            path = ob.getPhysicalPath()
            old_ob = ob
            ob = root.unrestrictedTraverse(path, None)
            if ob is None:
                self.log.debug("Object %r disappeard"%old_ob)
                # Let's use the old object for the notification info
                ob = v[0]['object']
            # Folderish document and parent has a notification
            # during the same transaction thus no notification
            parent = aq_parent(aq_inner(ob))
            if ((isinstance(parent, ProxyFolderishDocument) or
                 isinstance(parent, ProxyBTreeFolderishDocument)) and
                self._events.get(
                self._computeKeyFor(parent, k[0])) is not None):
                self.log.debug("Folderish child excluded")
            else:
                subtool = getToolByName(ob, 'portal_subscriptions', None)
                if subtool is not None:
                    self.log.debug("Processing event %s for %r with infos %r"
                    %(k[0], ob, v[1]))
                    subtool.notify_processed_event(k[0], ob, v[1])
                else:
                    self.log.error("Subscriptions Tool not found")
        self.log.debug("__call__ DONE")

def del_event_susbcriptions_manager():
    txn = transaction.get()
    setattr(txn, _EVT_MGR_ATTRIBUTE, None)

def get_event_subscriptions_manager():
    """Get the event susbcriptions manager.

    Creates it if needed.
    """
    txn = transaction.get()
    mgr = getattr(txn, _EVT_MGR_ATTRIBUTE, None)
    if mgr is None:
        mgr = EventSubscriptionsManager(
            get_before_commit_subscribers_manager())
        setattr(txn, _EVT_MGR_ATTRIBUTE, mgr)
    return mgr

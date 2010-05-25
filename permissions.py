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

__author__ = "Julien Anguenot <ja@nuxeo.com>"

"""CPS Subscriptions Permissions

  - 'Manage Subscriptions' : Manage subscriptions

  - 'Can subscribe' : user may subscribe

  - 'View My Subscriptions' : user may view all his subscriptions

  - 'Can Notify Content' : user may notify a document by hand
"""

from Products.CMFCore.permissions import setDefaultRoles

ManageSubscriptions = 'Manage Subscriptions'
setDefaultRoles( ManageSubscriptions, ('Manager'))

CanSubscribe = 'Can subscribe'
setDefaultRoles( CanSubscribe, ('Manager',))

ViewMySubscriptions = 'View My Subscriptions'
setDefaultRoles( ViewMySubscriptions, ('Manager', 'Member'))

CanNotifyContent = 'Can Notify Content'
setDefaultRoles( CanNotifyContent, ('Manager', 'Owner', 'Member'))

# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
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
"""Unit tests on BBB for CPSSubscriptions
"""

import unittest
import warnings

def warn(a, b):
    pass

from Products import CPSSubscriptions

# BBB : can be remove in CPS-3.6
from CPSSubscriptions import permissions

# XXX : Remove deprecation warnings for the tests
# waiting for the zope.deprecation of Zope3...
warnings.orig_warn = warnings.warn
warnings.warn = warn

from CPSSubscriptions import CPSSubscriptionsPermissions as old

# Restore back the warnings
warnings.warn = warnings.orig_warn

class CPSSubscriptionsBBBTestCase(unittest.TestCase):
    
    def test_BBB(self):
        self.assert_(permissions.ManageSubscriptions, old.ManageSubscriptions)
        self.assert_(permissions.CanSubscribe, old.CanSubscribe)
        self.assert_(permissions.ViewMySubscriptions, old.ViewMySubscriptions)
        self.assert_(permissions.CanNotifyContent, old.CanNotifyContent)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CPSSubscriptionsBBBTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

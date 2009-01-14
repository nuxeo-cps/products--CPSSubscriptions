# (C) Copyright 2008 Association Paris-Montagne
# (C) Copyright 2008 Association Viral Productions
# Author: Georges Racinet <georges@racinet.fr>
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
# $Id: testSubscriptionsTool.py 53340 2009-01-12 15:56:01Z gracinet $

import os
import sys

import unittest
from Products.CPSSubscriptions import upgrade
from Acquisition import aq_parent, aq_inner
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase

class TestUpgradesWithoutCPSSubscriptions(CPSTestCase):
    """Test upgrade steps if CPSSubscriptions profile hasn't been loaded
    """

    def afterSetUp(self):
        self.login('manager')

    def test_upgrade_347_348_email_from(self):
        upgrade.upgrade_347_348_email_from(self.portal)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUpgradesWithoutCPSSubscriptions))
    return suite

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

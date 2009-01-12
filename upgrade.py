# (C) Copyright 2008 Association Viral Productions <http://viral-prod.com>
# (C) Copyright 2008 Association Paris-Montagne <http://www.paris-montagne.org>
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
# $Id$

import logging
from Products.CMFCore.utils import getToolByName

def upgrade_347_348_email_from(portal):
    """Remove stored email_from addresses that have been copied from portal.

    See #
    """
    logger=logging.getLogger(
        'Products.CPSSubscriptions::upgrade_347_348_email_from')
    stool = getToolByName(portal, 'portal_subscriptions')
    global_mfrom = getToolByName(portal, 
                                 'portal_properties').email_from_address.strip()
    for container in stool._catalogSearchContainers():
        if container.mfrom.strip() == global_mfrom:
            container.mfrom = ''
            logger.info("Cleaned placeful container of %s", 
                        container.aq_inner.aq_parent)

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
from Products.CPSUtil.text import OLD_CPS_ENCODING

def upgrade_347_348_email_from(portal):
    """Remove stored email_from addresses that have been copied from portal.

    See #1925
    """
    logger = logging.getLogger(
        'Products.CPSSubscriptions::upgrade_347_348_email_from')

    stool = getToolByName(portal, 'portal_subscriptions', None)
    if stool is None:
        logger.warn(
            "CPSSubscriptions profile not loaded. Upgrade step is irrelevant.")
        return

    global_mfrom = getToolByName(portal,
                                 'portal_properties').email_from_address.strip()
    for container in stool._catalogSearchContainers():
        if container.mfrom.strip() == global_mfrom:
            container.mfrom = ''
            logger.info("Cleaned placeful container of %s",
                        container.aq_inner.aq_parent)


def upgrade_347_348_render_types_events(portal):
    """Initiate the compiled version of properties."""
    getToolByName(portal, 'portal_subscriptions')._postProcessProperties()


def upgrade_msg_unicode(portal):
    """Upgrade all messages to unicode"""

    logger = logging.getLogger(
        'Products.CPSSubscriptions::upgrade_msg_unicode')

    mappings = ('mapping_event_email_content', )
    strings = ('event_default_email_body',
               'event_default_email_title',
               'event_error_email_body',
               'subscribe_confirm_email_body',
               'subscribe_confirm_email_title',
               'unsubscribe_confirm_email_body',
               'unsubscribe_confirm_email_title',
               'subscribe_welcome_email_body',
               'subscribe_welcome_email_title',
               'unsubscribe_email_body',
               'unsubscribe_email_title',
               )
    stool = portal.portal_subscriptions
    stool._p_changed = 1
    count = 0

    for mapping in mappings:
        d = getattr(stool, mapping)
        for k, v in d.items():
            if isinstance(v, str):
                d[k] = v.decode(OLD_CPS_ENCODING)
                count += 1
            elif isinstance(v, list):
                for i, s in enumerate(v):
                    if isinstance(s, str):
                        v[i] = s.decode(OLD_CPS_ENCODING)
                        count += 1

    for attr in strings:
        v = getattr(stool, attr)
        if isinstance(v, str):
            setattr(stool, attr, v.decode(OLD_CPS_ENCODING))
            count += 1

    logger.info("Converted %s messages to unicode strings", count)

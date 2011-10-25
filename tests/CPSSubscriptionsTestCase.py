# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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

import email
from zope.interface import implements
from zope.app import zapi

from OFS.SimpleItem import SimpleItem
from Products.MailHost.interfaces import IMailHost

from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSDefault.tests.CPSTestCase import ExtensionProfileLayerClass


class LayerClass(ExtensionProfileLayerClass):
    extension_ids = ('CPSSubscriptions:default',)

CPSSubscriptionsLayer = LayerClass(__name__, 'CPSSubscriptionsLayer')

class DummyMailHost(SimpleItem):
    """Host that stores the sent mails in a list

    The list can then be inspected. This way you can see who got notified.
    """

    implements(IMailHost)

    mail_log = []

    def clearLog(self):
        self.mail_log = []

    def send(self, raw_message):
        message = email.message_from_string(raw_message)
        mfrom = message['From']
        mto = message['To']
        subject = message['Subject']
        bcc = message['Bcc']
        self.mail_log.append({'from': mfrom, 'to': mto, 'message': message,
                              'subject': subject, 'bcc': bcc})

    def _send(self, mfrom, mto, msg):
        message = email.message_from_string(msg)
        hfrom = message['From']
        hto = message['To']
        hcc = message['Cc']
        subject = message['Subject']
        if message['Bcc'] is not None:
            raise ValueError("Bcc has ended up in message headers")
        # True bcc computation: take effective mto minus To and Cc headers
        bcc = [r.strip() for r in mto]
        if hto:
            for r in hto.split(','):
                bcc.remove(r.strip())
        if hcc:
            for r in hto.split(','):
                bcc.remove(r.strip())
        bcc = ','.join(bcc)
        self.mail_log.append({'smtp_from': mfrom, 'smtp_to': mto, 
                              'message': message,
                              'from': hfrom, 'to': hto,
                              'subject': subject, 'bcc': bcc})


class CPSSubscriptionsTestCase(CPSTestCase):
    layer = CPSSubscriptionsLayer

    def afterSetUp(self):
        self._setupDummyMailHost()

    def _setupDummyMailHost(self):
        """Register the dummy mailhost instead of the standard one.

        No need to clean this up in beforeTearDown
        """
        self._mh = DummyMailHost()
        zapi.getSiteManager().registerUtility(self._mh, IMailHost)
        self._mh.clearLog()


# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Copyright (c) 2004 CGEY <http://cgey.com>
# Copyright (c) 2004 Ministère de L'intérieur (MISILL)
#               <http://www.interieur.gouv.fr/>
# Authors : Julien Anguenot <ja@nuxeo.com>
#           Florent Guillaume <fg@nuxeo.com>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# $Id$

__author__ = "Julien Anguenot <mailto:ja@nuxeo.com>"

""" Notification rule classes

The something that is actually done.  Usually it involves Recipients (sending
email) but that's not mandatory (triggering an arbitrary script for instance).

Notifications are subclasses of NotificationRule and store also as
subobjects, like RecipientsRule.

"""

from Globals import InitializeClass, MessageDialog
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.PortalFolder import PortalFolder

from zLOG import LOG, INFO, DEBUG

class NotificationRule(PortalFolder):
    """Base Notification rule Class.

    All the Notifications will sub-class this one and implement a notification
    type.
    """

    def notifyRecipients(self, **kw):
        """ Notify recipients

        This method will be called by the Subscription object.
        """
        raise NotImplementedError

InitializeClass(NotificationRule)

################################################################

class MailNotificationRule(NotificationRule):
    """Mail Notification Rule

    Sending mail to the recipients of the subscription.
    Only one MailNotifcationRule is necessarly within a subscription.
    """

    meta_type = "Mail Notification Rule"
    portal_type = meta_type

    security = ClassSecurityInfo()

    def _getMailFrom(self, object):
        """ Return an email for the mail from field of the mail.

        1 - Creator of the object if an object has been created.
        2 - CPS Administator.
        3 - Others ?
        """

        mtool = self.portal_membership
        creator = object.Creator()
        creator_user = mtool.getMemberById(creator)

        returned_email = ''
        if creator_user:
            email_creator = creator_user.getProperty('email')
            if email_creator is not None:
                returned_email = email_creator
        else:
            pprops = self.portal_properties
            cps_admin_email = getattr(pprops,
                                      'email_from_address',
                                      'no_mail@no_mail.com')
            returned_email = cps_admin_email

        # FIXME
        if returned_email:
            return returned_email
        else:
            return 'no_mail@no_mail.com'

    def _getSubject(self, infos):
        """ Returns the subject of the email.

        Is proccessed with the infos given as parameters.
        """

        try:
            subject = self.portal_subscriptions.getDefaultMessageTitle(
                event_id=infos['event']) %infos
        except (KeyError,):
            # If the user put wrong variables
            subject = "No Subject"

        return subject

    def _getBody(self, infos):
        """ Returns the body of the email.

        Is proccessed with the infos given as parameters.
        """

        try:
            body = self.portal_subscriptions.getDefaultMessageBody(
                event_id=infos['event']) %infos
        except (KeyError,):
            # If the user put wrong variables
            body = self.portal_subscriptions.getErrorMessageBody()

        return body

    def _makeInfoDict(self, event_type, object):
        """Building the infos dict used for processing the email.
        """

        infos = {}

        portal_subscriptions = getToolByName(self, 'portal_subscriptions')
        mcat = self.Localizer.default

        events_from_context = portal_subscriptions.getEventsFromContext(
            context=aq_parent(aq_inner(object)))

        # Just more secure in case of the event configuration is badly done.
        if events_from_context is None:
            return {}
        event_from_context = mcat(events_from_context.get(event_type,
                                                          event_type)).encode("ISO-8859-15",
                                                                              'ignore')

        infos['portal_title'] = self.portal_url.getPortalObject().Title()
        infos['notification_title'] = event_from_context
        infos['event'] = event_type

        infos['object_title'] = object.Title()
        infos['object_url'] = object.absolute_url()
        infos['object_type'] = getattr(object, 'portal_type', '')

        infos['user_id'] = object.Creator()
        infos['user_name'] = getattr(self.portal_membership.getMemberById(
            object.Creator()), 'fullname', '')
        return infos

    security.declareProtected(ManagePortal, "notifyRecipients")
    def notifyRecipients(self, event_type, object,
                         infos=None, emails=[], members=[], groups=[], **kw):
        """ Notify recipients

        This method will be called by the Subscription object.
        """

        #
        # Dealing only with emails right now.
        # to implement : members and groups
        #

        infos = self._makeInfoDict(event_type, object)

        if not infos:
            return

        LOG(":: CPSSubscriptions :: MailNotificationRule :: on",
            INFO,
            infos)

        mfrom = self._getMailFrom(object)
        subject = self._getSubject(infos)
        body = self._getBody(infos)

        for email in emails:
            LOG("::MailNotificationRule :: SENDING MAIL :: TO ",
                INFO,
                email)
            self.MailHost.send(messageText=body,
                               mto=[email],
                               mfrom=mfrom,
                               subject=subject,)

InitializeClass(MailNotificationRule)

def addMailNotificationRule(self, id=None, title='', REQUEST=None, **kw):
    """Add a Mail Notification Rule object type
    """

    id = self.portal_subscriptions.getMailNotificationRuleObjectId()
    title = 'NOTIFICATION RULE'

    if hasattr(aq_base(self), id):
        return MessageDialog(
            title='Item Exists',
            message='This object already contains an %s' % ob.id,
            action='%s/manage_main' % REQUEST['URL1'])

    ob = MailNotificationRule(id, title=title, **kw)
    self._setObject(id, ob)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main')

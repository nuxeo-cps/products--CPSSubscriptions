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

import cStringIO
import string
import quopri
import mimify
import mimetools
import MimeWriter

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

    def getSMTPServerName(self):
        """Returns the name of the SMTP server
        """
        return self.MailHost.smtp_host

    def getSMTPServerPort(self):
        """Returns the port for the smtp host
        """
        return self.MailHost.smtp_port

    def getRawMessage(self, infos):
        """ Renders an RFC822 compliant message.
        """

        rendered_message = cStringIO.StringIO()
        writer = MimeWriter.MimeWriter(rendered_message)

        # Sender
        sender = "%s <%s>" % (infos['sender_email'], infos['sender_email'])
        writer.addheader('From', sender)

        # Subject
        subj = infos['subject']
        infp = cStringIO.StringIO(subj)
        outfp = cStringIO.StringIO()
        quopri.encode(infp, outfp, 1)
        subject = outfp.getvalue()
        subject = string.replace(subject, "\n", "")
        subject = string.replace(subject, " ", "_")

        # Header
        if string.find(subject, "?") == -1:
            # FIXME
            #subject = "=?iso-8859-1?Q?%s?=" % subject
            pass
        else:
            # FIXME
            #subject = string.replace(subject, "?", "=3F")
            #subject = "=?iso-8859-1?Q?%s?=" % subject
            pass
        writer.addheader('subject', subject)

        # To
        writer.addheader(string.capitalize('to'),
                         mimify.mime_encode_header(infos['to']))

        # Misc
        writer.addheader('X-Mailer', 'Nuxeo CPS : CPSSubscriptions')

        writer.flushheaders()
        writer._fp.write('Content-Transfer-Encoding: quoted-printable\n')
        body_writer = writer.startbody('text/plain;',
                                       [],
                                       {'Content-Transfer-Encoding':
                                        'quoted-printable'})

        body = '\n'+infos['body']
        body = cStringIO.StringIO(body)
        body.seek(0)
        mimetools.copyliteral(body, body_writer)

        return rendered_message.getvalue()


    def sendMail(self, mail_infos):
        """Send a mail

        mail_infos contains all the needed information
        """

        raw_message = self.getRawMessage(mail_infos)

        LOG(":: CPSSubscriptions :: sendMail() :: for",
            INFO,
            mail_infos)

        self.MailHost.send(raw_message)

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

    def _makeInfoDict(self, event_type, object, infos={}):
        """Building the infos dict used for processing the email.
        """

        portal_subscriptions = getToolByName(self, 'portal_subscriptions')
        mcat = self.Localizer.default

        events_from_context = portal_subscriptions.getEventsFromContext(
            context=aq_parent(aq_inner(object)))

        # Just more secure in case of the event configuration is badly done.
        if events_from_context is None:
            return {}
        event_from_context = mcat(
            events_from_context.get(event_type,
                                    event_type)).encode("ISO-8859-15",
                                                        'ignore')

        infos['portal_title'] = self.portal_url.getPortalObject().Title()
        infos['notification_title'] = event_from_context
        infos['event'] = event_type

        infos['object_title'] = object.Title()
        infos['object_url'] = infos.get('url', object.absolute_url())
        infos['object_parent_title'] = aq_parent(aq_inner(object)).Title()
        infos['object_type'] = getattr(object, 'portal_type', '')

        infos['user_id'] = object.Creator()
        infos['user_name'] = getattr(self.portal_membership.getMemberById(
            object.Creator()), 'fullname', '')

        return infos

    ##################################################################
    ##################################################################

    security.declareProtected(ManagePortal, "notifyRecipients")
    def notifyRecipients(self,
                         event_type,
                         object,
                         infos=None,
                         emails=[],
                         members=[],
                         groups=[],
                         **kw):
        """ Notify recipients

        This method will be called by the Subscription object when a
        notification occurs.
        """

        portal = getToolByName(self,'portal_url').getPortalObject()

        infos = self._makeInfoDict(event_type, object, infos)
        mfrom = self._getMailFrom(object)
        subject = self._getSubject(infos)
        body = self._getBody(infos)

        LOG(":: CPSSubscriptions :: MailNotificationRule :: on",
            INFO,
            infos)

        # Dealing with emails
        for email in emails:
            mail_infos = {}
            mail_infos['sender_name'] = portal.Title()
            mail_infos['sender_email'] = mfrom
            mail_infos['subject'] = subject
            mail_infos['to'] = email
            mail_infos['body'] = body

            self.sendMail(mail_infos)

        # Dealing with members
        for member in members:
            pass

        # Dealing with groups
        for group in groups:
            pass

    #####################################################################
    #####################################################################

    security.declareProtected(ManagePortal, "notifyConfirmSubscription")
    def notifyConfirmSubscription(self, event_id, object, email, context):
        """ Mail notification for subscription

        This method is called when soemone want to subscribe
        """

        tool = getToolByName(self, 'portal_subscriptions')
        container = tool.getSubscriptionContainerFromContext(context)
        portal = getToolByName(self,'portal_url').getPortalObject()
        object_url = context.absolute_url() \
                     + '/folder_confirm_subscribe_form?fake=subscriptions' \
                     + '&event_id='\
                     + event_id \
                     + '&email='\
                     + email

        # Pre process for body/subject
        infos = {'portal_title': portal.Title(),
                 'object_url'  : repr(object_url),
                 'event_id'    : event_id,
                 'email'       : email,
                 'mfrom'       : container.getMailFrom()}

        subject = tool.getSubscribeConfirmEmailTitle() %infos
        body = tool.getSubscribeConfirmEmailBody() %infos

        # For building the E-Mail
        mail_infos = {}
        mail_infos['sender_name'] = infos.get('portal_title')
        mail_infos['sender_email'] = infos.get('mfrom', 'no_mail@no_mail.com')
        mail_infos['subject'] = subject
        mail_infos['to'] = email
        mail_infos['body'] = body

        # Send mail then.
        self.sendMail(mail_infos)

    security.declareProtected(ManagePortal, "notifyWelcomeSubscription")
    def notifyWelcomeSubscription(self, event_id, object, email, context):
        """ Mail notification for subscription welcome message

        This method is called when someone just subscribe
        """

        tool = getToolByName(self, 'portal_subscriptions')
        portal = getToolByName(self,'portal_url').getPortalObject()
        container = tool.getSubscriptionContainerFromContext(context)

        info_url = context.absolute_url() + '/folder_subscribe_form'
        object_url = context.absolute_url()

        # Pre process for body/subject
        infos = {'portal_title': portal.Title(),
                 'object_url'  : object_url,
                 'object_title': context.title_or_id(),
                 'info_url'    : info_url,
                 'event_id'    : event_id,
                 'email'       : email,
                 'mfrom'       : container.getMailFrom()}

        subject = tool.getSubscribeWelcomeEmailTitle() %infos
        body = tool.getSubscribeWelcomeEmailBody() %infos

        # Post process
        infos['body'] =  body
        infos['subject'] = subject.replace('\n', '')

        # For building the E-Mail
        mail_infos = {}
        mail_infos['sender_name'] = infos.get('portal_title')
        mail_infos['sender_email'] = infos.get('mfrom', 'no_mail@no_mail.com')
        mail_infos['subject'] = infos.get('subject', 'No Subject')
        mail_infos['to'] = email
        mail_infos['body'] = infos.get('body', '')

        # Send mail then.
        self.sendMail(mail_infos)

    ###################################################################
    ###################################################################

    security.declareProtected(ManagePortal, "notifyUnSubscribe")
    def notifyUnSubscribe(self, event_id, object, email, context):
        """ Mail notification for unsubscription message

        This method is called when someone just unsubscribe
        """

        tool = getToolByName(self, 'portal_subscriptions')
        portal = getToolByName(self,'portal_url').getPortalObject()
        container = tool.getSubscriptionContainerFromContext(context)

        info_url = context.absolute_url() + '/folder_subscribe_form'
        object_url = context.absolute_url()

        # infos contains information needed to generated messages
        infos = {'portal_title': portal.Title(),
                 'object_url'  : object_url,
                 'object_title': context.title_or_id(),
                 'info_url'    : info_url,
                 'event_id'    : event_id,
                 'email'       : email,
                 'mfrom'       : container.getMailFrom()}

        subject = tool.getUnSubscribeEmailTitle() %infos
        body = tool.getUnSubscribeEmailBody() %infos

        # Post process
        infos['body'] =  body
        infos['subject'] = subject.replace('\n', '')

        # For building the E-Mail
        mail_infos = {}
        mail_infos['sender_name'] = infos.get('portal_title')
        mail_infos['sender_email'] = infos.get('mfrom', 'no_mail@no_mail.com')
        mail_infos['subject'] = infos.get('subject', 'No Subject')
        mail_infos['to'] = email
        mail_infos['body'] = infos.get('body', '')

        # Send mail then.
        self.sendMail(mail_infos)

    security.declareProtected(ManagePortal, "notifyConfirmUnSubscribe")
    def notifyConfirmUnSubscribe(self, event_id, object, email, context):
        """ Mail notification for confirm unsubscription message

        This method is called when someone just confirm the unsubscription
        """

        tool = getToolByName(self, 'portal_subscriptions')
        portal = getToolByName(self,'portal_url').getPortalObject()
        container = tool.getSubscriptionContainerFromContext(context)

        info_url = context.absolute_url() + '/folder_subscribe_form'
        object_url = context.absolute_url()
        url = context.absolute_url() \
              + '/folder_confirm_unsubscribe_form?fake=subscriptions' \
              '&event_id='\
              + event_id \
              + '&email='\
              + email

        # infos contains information needed to generated messages
        infos = {'portal_title': portal.Title(),
                 'object_url'  : object_url,
                 'url'         : url,
                 'object_title': context.title_or_id(),
                 'info_url'    : info_url,
                 'event_id'    : event_id,
                 'email'       : email,
                 'mfrom'       : container.getMailFrom()}

        subject = tool.getUnSubscribeConfirmEmailTitle() %infos
        body = tool.getUnSubscribeConfirmEmailBody() %infos

        # Post process
        infos['body'] =  body
        infos['subject'] = subject.replace('\n', '')

        # For building the E-Mail
        mail_infos = {}
        mail_infos['sender_name'] = infos.get('portal_title')
        mail_infos['sender_email'] = infos.get('mfrom', 'no_mail@no_mail.com')
        mail_infos['subject'] = infos.get('subject', 'No Subject')
        mail_infos['to'] = email
        mail_infos['body'] = infos.get('body', '')

        # Send mail then.
        self.sendMail(mail_infos)

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

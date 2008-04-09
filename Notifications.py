# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004-2008 Nuxeo SAS <http://nuxeo.com>
# Copyright (c) 2004 CGEY <http://cgey.com>
# Copyright (c) 2004 Ministere de L'interieur (MISILL)
#               <http://www.interieur.gouv.fr/>
# Authors : Julien Anguenot <ja@nuxeo.com>
#           Florent Guillaume <fg@nuxeo.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# $Id$

__author__ = "Julien Anguenot <mailto:ja@nuxeo.com>"

"""Notification rule classes

The something that is actually done.  Usually it involves Recipients (sending
email) but that's not mandatory (triggering an arbitrary script for instance).

Notifications are subclasses of NotificationRule and store also as
subobjects, like RecipientsRule.
"""

import socket
import cStringIO
import string
import mimify
import mimetools
import MimeWriter
from smtplib import SMTPException
from urllib import urlencode

from AccessControl import getSecurityManager
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner
from Globals import InitializeClass
from Globals import MessageDialog

from Products.MailHost.MailHost import MailHostError

from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.PortalFolder import PortalFolder

from logging import getLogger

logger = getLogger('CPSSubscriptions.Notifications')

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

    def getParentSubscription(self):
        """Return the parent subscription
        """
        return aq_parent(aq_inner(self))

    def getSubscriptionContainer(self):
        """Return the placefull subscription container this notification is in.

        A notification is supposed to be into a 'Subscription Configuration'
        object, itself in a 'PlaceFull Subscription Container' object.
        """
        res = None
        subscription = self.getParentSubscription()
        if subscription is not None:
            container = subscription.getParentContainer()
            if container is not None:
                res = container
        return res

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

    def getRawMessage(self, infos, object, event_id):
        """ Renders an RFC822 compliant message.
        """

        rendered_message = cStringIO.StringIO()
        writer = MimeWriter.MimeWriter(rendered_message)

        # Sender
        if infos.get('sender_name'):
            sender = '"%s" <%s>' % (infos['sender_name'],
                                    infos['sender_email'])
        else:
            sender = '"%s" <%s>' % (infos['sender_email'],
                                    infos['sender_email'])
        writer.addheader('From', sender)

        # Reply-To
        reply_to_email = infos.get('reply_to_email')
        if reply_to_email is not None:
            reply_to_name = infos.get('reply_to_name', reply_to_email)
            reply_to = '"%s" <%s>' % (reply_to_name, reply_to_email)
            writer.addheader('Reply-To', reply_to)

        # Subject
        subject = infos['subject']
        subject = string.replace(subject, '\n', '')

        # Header
        writer.addheader('subject', subject)

        # To
        if infos.get('to'):
            writer.addheader(string.capitalize('to'),
                             mimify.mime_encode_header(infos['to']))
        # Bcc
        if infos.get('bcc'):
            writer.addheader(string.capitalize('bcc'),
                             mimify.mime_encode_header(infos['bcc']))

        # Misc
        writer.addheader('X-Mailer', 'Nuxeo CPS 3 : CPSSubscriptions')
        writer.flushheaders()
        writer._fp.write('Content-Transfer-Encoding: 8bit\n')

        if infos['body'][1] == 'text/html':
            body_writer = writer.startbody('text/html; charset=iso-8859-15',
                                           [],
                                           {'Content-Transfer-Encoding':
                                            '8bit'})
        else:
            body_writer = writer.startbody('text/plain; charset=iso-8859-15',
                                           [],
                                           {'Content-Transfer-Encoding':
                                            '8bit'})

        body = '\n' + infos['body'][0]
        body = cStringIO.StringIO(body)
        body.seek(0)
        mimetools.copyliteral(body, body_writer)

        return rendered_message.getvalue()

    def _validateStructure(self, mail_infos):
        """Validate the mail_infos structure
        """
        return  (isinstance(mail_infos.get('sender_email'), str) and
                 # It is possible that no 'to' nor 'bcc' fields are specified
                 isinstance(mail_infos.get('to', ''), str) and
                 isinstance(mail_infos.get('bcc', ''), str) and
                 isinstance(mail_infos.get('subject'), str) and
                 isinstance(mail_infos.get('body'), tuple) and
                 len(mail_infos.get('body')) == 2)

    def sendMail(self, mail_infos, object=None, event_id=None, mailhost=None):
        """Send a mail

        mail_infos contains all the needed information
        """
        # Check the mail structure
        if not self._validateStructure(mail_infos):
            logger.error("sendMail() check the email of the recipients %r",
                         mail_infos)
            return -1

        raw_message = self.getRawMessage(mail_infos, object, event_id)

        logger.debug("sendMail() sending:\n\n%s", raw_message)

        try:
            if mailhost is not None:
                mailhost.send(raw_message)
            else:
                self.MailHost.send(raw_message)
        except (socket.error, MailHostError, SMTPException), e:
            logger.debug("sendMail() Error while sending mail "
                         "check your SMTP parameters or mailfrom address "
                         "error was:\n%r", e)

    def _getMailSenderInfo(self, infos):
        """Return mail sender information (name and email)

        Try to get email from infos and from the subscriptions container
        instead of default values.
        """
        # default values: admin name, admin email
        substool = getToolByName(self, 'portal_subscriptions')
        # XXX AT: maybe use the portal title instead of the portal admin
        # name to send the email (?)
        sender_email, sender_name = substool.getMailSenderInfo()
        logger.debug('_getMailSenderInfo from substool: %s, %s',
                   sender_name, sender_email)
        # get info from 'infos' dict
        if infos.has_key('mfrom'):
            sender_email = infos.get('mfrom')
            logger.debug('_getMailSenderInfo from mfrom key in infos: %s, %s',
                         sender_name, sender_email)
        # get from container
        container = self.getSubscriptionContainer()
        if container is not None:
            sender_email = container.getMailFrom()
            logger.debug('_getMailSenderInfo from container property: %s, %s',
                         sender_name, sender_email)
        return sender_email, sender_name

    def _getSubject(self, infos):
        """ Returns the subject of the email.

        Is proccessed with the infos given as parameters.
        """

        _translation_table = string.maketrans(
            r"""ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöøùúûüýÿ""",
            r"""AAAAAACEEEEIIIINOOOOOOUUUUYaaaaaaceeeeiiiinoooooouuuuyy""")

        try:
            subject = self.portal_subscriptions.getDefaultMessageTitle(
                event_id=infos['event']) % infos
            # Temporary fix for suppressing accented chars, old Mime
            # modules of Python can't hndle properly non-ASCII in
            # subject header.
            subject = subject.translate(_translation_table)
        except (KeyError, TypeError), e:
            logger.error("Error in subject notification template for %r: %s",
                         infos.get('event'), e)
            # If the user put wrong variables
            subject = "No Subject"

        return subject

    def _getBody(self, infos):
        """ Returns the body of the email.

        Is proccessed with the infos given as parameters.
        """
        try:
            body = self.portal_subscriptions.getDefaultMessageBody(
                event_id=infos['event']) % infos
        except (KeyError, TypeError, ValueError), e:
            logger.error("Error in body notification template with infos %r: %r",
                         infos, e)
            # If the user put wrong variables
            body = self.portal_subscriptions.getErrorMessageBody()
        return body

    def _makeInfoDict(self, event_type, object, infos=None):
        """Build the info dict used for processing the email.

        Additional keys are added to the infos dictionnary provided by the
        event notification.
        """
        if infos is None:
            infos = {}

        stool = getToolByName(self, 'portal_subscriptions')
        members = getToolByName(self, 'portal_directories').members
        ttool = getToolByName(self, 'portal_types')

        context = aq_parent(aq_inner(object))
        mcat = self.translation_service

        events_from_context = stool.getEventsFromContext(context)

        # Just more secure in case of the event configuration is badly done.
        if not events_from_context:
            return {}

        event_type_trsl = mcat(events_from_context.get(event_type, event_type))
        if event_type_trsl is not None:
            event_type_trsl = event_type_trsl.encode('ISO-8859-15', 'ignore')
        else:
            event_type_trsl = event_type

        event_from_context = event_type_trsl

        portal = self.portal_url.getPortalObject()
        infos['portal_url'] = portal.absolute_url()
        infos['portal_title'] = portal.Title()
        infos['info_url'] = context.absolute_url() + '/folder_subscribe_form'
        infos['notification_title'] = event_from_context
        infos['event'] = event_type

        infos['object_title'] = object.Title()
        infos['object_url'] = infos.get('url', object.absolute_url())
        infos['object_type'] = getattr(object, 'portal_type', '')

        # i18n type title
        type_title = ttool[infos['object_type']].Title()
        i18n_type_title = mcat(type_title)
        if i18n_type_title is not None:
            i18n_type_title = i18n_type_title.encode('ISO-8859-15', 'ignore')
            if  i18n_type_title != type_title:
                infos['object_type'] = i18n_type_title

        object_parent = aq_parent(aq_inner(object))
        infos['object_parent_title'] = object_parent.Title()
        infos['object_parent_url'] = object_parent.absolute_url()

        object_creator_id = object.Creator()
        object_creator_user = members.getEntry(object_creator_id, default=None)
        object_creator_name = ''
        if object_creator_user:
            object_creator_name = object_creator_user.get('fullname')
        infos['object_creator_id'] = object_creator_id
        infos['object_creator_name'] = object_creator_name

        # Including the object attributes so that user can use them
        # within the notification messages too.
        try:
            rep_ob = object.getContent()
            schema = rep_ob.getTypeInfo().getDataModel(rep_ob, object)
            for attr, value in schema.items():
                infos[attr] = value
        except AttributeError:
            # Not a Flexible Type Information
            for attr, value in object.__dict__.items():
                if not attr.startswith('_'):
                    infos[attr] = value

        # Including information about the user whose action is at the origin of
        # the event.
        user_id = getSecurityManager().getUser().getId()
        user = members.getEntry(user_id, default=None)
        user_name = ''
        if user:
            user_name = user.get('fullname')
        infos['user_id'] = user_id
        infos['user_name'] = user_name

        # Making sure that there is always an available "comments"
        # variable so that this variable is always available for all
        # email message bodies and thus will prevent producing
        # KeyError errors.
        if infos.get('comments') is None:
            infos['comments'] = ''

        # Including kwargs that are added by the workflow. We are especially
        # interested in the transition comments of the workflow. If those
        # transition comments from the workflow exist we use them as the
        # comments variable.
        for k, v in infos.get('kwargs', {}).items():
            infos['kwargs_' + k] = v
        if infos.get('kwargs_comment') is not None:
            infos['comments'] = infos['kwargs_comment']
        if infos.get('kwargs_comments') is not None:
            infos['comments'] = infos['kwargs_comments']

        logger.debug("_makeInfoDict() available infos in emails: %r", infos)
        return infos

    security.declareProtected(ManagePortal, 'notifyRecipients')
    def notifyRecipients(self, event_type, object_, infos=None, emails=[],
                         members=[], groups=[], **kw):
        """Notify recipients

        This method will be called by the Subscription object when a
        notification occurs.

        This method id aware about the fact that for some recipients
        we won't send a email directly but store the email for further
        scheduling. (daily, monthly, ...)
        """

        # Construct a mapping for the email notification
        infos = self._makeInfoDict(event_type, object_, infos)
        if not infos:
            # No notification info for that object
            return

        # Let's check if we render the content, instead of a regular
        # user defined notification message, because of the
        # portal_type or because of the event id.  This is defined
        # subscriptions tool side.
        stool = getToolByName(self, 'portal_subscriptions')
        rendered_ptypes = stool.getRenderedPortalTypes()
        rendered_events = stool.getRenderedEvents()
        if (object_ is not None and
            getattr(object_, 'portal_type', '') in rendered_ptypes or
            infos.get('event', '') in rendered_events):
            # Is the object_ a CPSDocument ?
            doc = hasattr(object_, 'getContent') and object_.getContent()
            if hasattr(doc, 'render'):
                body = doc.render(proxy=object_)
                mime_type = 'text/html'
            else:
                # XXX : we might handle whatever sort of content for rendering
                # in here. Using the main_template flag maybe.
                body = self._getBody(infos)
                mime_type = 'text/plain'
        else:
            body = self._getBody(infos)
            mime_type = 'text/plain'

        # Save the email notification body for furher scheduling.
        # The scheduling table is stored on the subscriptions tool for now.
        archive_id = stool.addNotificationMessageBodyObject(body, mime_type)

        # Filter for the recipients we need to notify `real time` For
        # the other ones, we will add an entry within the scheduling
        # table
        real_time = []
        for email in emails:
            container = stool.getSubscriptionContainerFromContext(self)
            user_mode = container.getUserMode(email)
            if user_mode != 'mode_real_time':
                stool.scheduleNotificationMessageFor(user_mode, email,
                                                     archive_id)
            else:
                real_time.append(email)

        # Send all the emails in batches for those in `real time` mode
        max_recipients = stool.max_recipients_per_notification
        semail, sname = self._getMailSenderInfo(infos)
        while real_time:
            batch = real_time[:max_recipients]
            real_time = real_time[max_recipients:]
            bcc = ','.join(batch)
            mail_infos = {
                'sender_name': sname,
                'sender_email': semail,
                'subject': self._getSubject(infos),
                # No 'to' field here, the many recipients
                # are specified in the 'bcc' field.
                'bcc': bcc,
                'body': (body, mime_type),
                }
            self.sendMail(mail_infos, object_, event_id=infos.get('event', ''))
            logger.debug('notifyRecipients() %r', mail_infos)

        # TODO: Dealing with members
        for member in members:
            pass

        # TODO: Dealing with groups
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
        url_args = {
            'fake': 'subscriptions',
            'event_id': event_id,
            'email': email,
            }
        url_args = urlencode(url_args)
        object_url = context.absolute_url() \
                     + "/folder_confirm_subscribe_form?%s" %(url_args,)

        # Pre process for body/subject
        infos = {
            'portal_title': portal.Title(),
            'object_url'  : object_url,
            'event_id'    : event_id,
            'email'       : email,
            'mfrom'       : container.getMailFrom(),
            }

        subject = tool.getSubscribeConfirmEmailTitle() % infos
        body = tool.getSubscribeConfirmEmailBody() % infos
        semail, sname = self._getMailSenderInfo(infos)

        # For building the E-Mail
        mail_infos = {
            'sender_name': sname,
            'sender_email': semail,
            'subject': subject,
            'to': email,
            'body': (body, 'text/plain'),
            }

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
        infos = {
            'portal_title': portal.Title(),
            'object_url'  : object_url,
            'object_title': context.title_or_id(),
            'info_url'    : info_url,
            'event_id'    : event_id,
            'email'       : email,
            'mfrom'       : container.getMailFrom(),
            }

        subject = tool.getSubscribeWelcomeEmailTitle() % infos
        body = tool.getSubscribeWelcomeEmailBody() % infos
        semail, sname = self._getMailSenderInfo(infos)

        # Post process
        infos['body'] =  body
        infos['subject'] = subject.replace('\n', '')

        # For building the E-Mail
        mail_infos = {
            'sender_name': sname,
            'sender_email': semail,
            'subject': infos.get('subject', 'No Subject'),
            'to': email,
            'body': (infos.get('body', ''), 'text/plain'),
            }
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
        infos = {
            'portal_title': portal.Title(),
            'object_url'  : object_url,
            'object_title': context.title_or_id(),
            'info_url'    : info_url,
            'event_id'    : event_id,
            'email'       : email,
            'mfrom'       : container.getMailFrom(),
            }

        subject = tool.getUnSubscribeEmailTitle() % infos
        body = tool.getUnSubscribeEmailBody() % infos
        semail, sname = self._getMailSenderInfo(infos)

        # Post process
        infos['body'] =  body
        infos['subject'] = subject.replace('\n', '')

        # For building the E-Mail
        mail_infos = {
            'sender_name': sname,
            'sender_email': semail,
            'subject': infos.get('subject', 'No Subject'),
            'to': email,
            'body': (infos.get('body', ''), 'text/plain'),
            }

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
        url_args = {
            'fake': 'subscriptions',
            'event_id': event_id,
            'email': email,
            }
        url_args = urlencode(url_args)
        object_url = context.absolute_url() \
                     + "/folder_confirm_unsubscribe_form?%s" %(url_args,)

        # infos contains information needed to generated messages
        infos = {
            'portal_title': portal.Title(),
            'object_url'  : object_url,
            'url'         : info_url,
            'object_title': context.title_or_id(),
            'info_url'    : info_url,
            'event_id'    : event_id,
            'email'       : email,
            'mfrom'       : container.getMailFrom(),
            }

        subject = tool.getUnSubscribeConfirmEmailTitle() % infos
        body = tool.getUnSubscribeConfirmEmailBody() % infos
        semail, sname = self._getMailSenderInfo(infos)

        # Post process
        infos['body'] =  body
        infos['subject'] = subject.replace('\n', '')

        # For building the E-Mail
        mail_infos = {
            'sender_name': sname,
            'sender_email': semail,
            'subject': infos.get('subject', 'No Subject'),
            'to': email,
            'body': (infos.get('body', ''), 'text/plain'),
            }
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

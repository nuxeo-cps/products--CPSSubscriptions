##parameters=REQUEST=None, **kw
# $Id$
"""Send a email for custom notifications

kws should contain:
members, explicit_recipients_emails, mail_subject, mail_body
"""

from Products.CMFCore.utils import getToolByName
from Products.CPSUtil.text import get_final_encoding

if REQUEST is not None:
    kw.update(REQUEST.form)

members = kw.get('members', [])
explicit_recipients_emails = kw.get('explicit_recipients_emails', [])
mail_subject = kw.get('mail_subject', '')
mail_body = kw.get('mail_body', '')

mcat = context.translation_service
encoding = get_final_encoding(mcat)

# Add a link to the current content at the end of the mail_body
mail_body = mail_body + \
            '\n' + \
            mcat('label_notification_related_document').encode(encoding,
                                                               'ignore') + \
            ' : ' + \
            context.absolute_url()

mtool = getToolByName(context, 'portal_membership')
member = mtool.getAuthenticatedMember()
reply_to_email = mtool.getEmailFromUsername(member.getUserName())
reply_to_name = member.getProperty('sn') + ' ' + member.getProperty('givenName')

subtool = getToolByName(context, 'portal_subscriptions')
sender_email, sender_name = subtool.getMailSenderInfo()

tos = explicit_recipients_emails or []
for member_id in members:
    email = mtool.getEmailFromUsername(member_id)
    if email is not None:
        tos.append(email)

infos = {
    'sender_email'   : sender_email,
    'sender_name'    : sender_name,
    'reply_to_email' : reply_to_email,
    'reply_to_name'  : reply_to_name,
    'body'           : (mail_body, 'text/plain'),
    'subject'        : mail_subject,
    'to'             : ','.join(tos),
    }

cerror = subtool.sendmail(infos=infos)

if REQUEST is not None:
    psm = 'psm_an_email_has_been_sent'
    redirect_url = REQUEST['URL1'] + '?portal_status_message=%s' % psm
    return REQUEST.RESPONSE.redirect(redirect_url)


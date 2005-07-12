##parameters=REQUEST=None, **kw
# $Id$
"""Send a email for custom notifications

kws should contain:
members, explicit_recipients_emails, mail_subject, mail_body
"""

from Products.CMFCore.utils import getToolByName

if REQUEST is not None:
    kw.update(REQUEST.form)

members = kw.get('members', [])
explicit_recipients_emails = kw.get('explicit_recipients_emails', [])
mail_subject = kw.get('mail_subject', '')
mail_body = kw.get('mail_body', '')

mcat = context.translation_service

# Add a link to the current content at the end of the mail_body
mail_body = mail_body + \
            '\n' + \
            mcat('label_notification_related_document').encode('ISO-8859-15', 'ignore') + \
            ' : ' + \
            context.absolute_url()

mtool = getToolByName(context, 'portal_membership')
member = mtool.getAuthenticatedMember()
sender_email = member.getProperty('email')
sender_name = member.getProperty('sn') + ' ' + member.getProperty('givenName')

subtool = getToolByName(context, 'portal_subscriptions')
def_semail, def_sname = subtool.getMailSenderInfo()

if not sender_email:
    sender_email = def_semail
    sender_name = def_sname

tos = explicit_recipients_emails
for member_id in members:
    tos.append(context.getMemberEmail(member_id))

to_str = ''
for to in tos:
    to_str += to + ','

infos = {
    'sender_email' : sender_email,
    'sender_name'  : sender_name,
    'body'         : (mail_body, 'text/plain'),
    'subject'      : mail_subject,
    'to'           : to_str[:len(to_str)-1],
    }

cerror = subtool.sendmail(infos=infos)

if REQUEST is not None:
    psm = 'psm_an_email_has_been_sent'
    redirect_url = REQUEST['URL1'] + '?portal_status_message=%s' %psm
    return REQUEST.RESPONSE.redirect(redirect_url)

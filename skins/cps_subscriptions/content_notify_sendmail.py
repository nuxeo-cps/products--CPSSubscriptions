##parameters=REQUEST=None, **kw


if REQUEST is not None:
    form = REQUEST.form
    members = form.get('members', [])
    explicit_recipients_emails = form.get('explicit_recipients_emails', [])
    mail_subject = form.get('mail_subject', '')

    #
    # Add a link to the current content at the end of the mail_body
    #

    mcat = context.Localizer.default

    mail_body = form.get('mail_body', '')
    mail_body = mail_body + \
                '\n' + \
                mcat('label_notification_related_document').encode('ISO-8859-15', 'ignore') + \
                ' : ' + \
                context.absolute_url()

    mtool = context.portal_membership
    member = mtool.getAuthenticatedMember()
    sender_email = member.getProperty('email')

    tos = explicit_recipients_emails
    for member_id in members:
        tos.append(context.getMemberEmail(member_id))

    to_str = ''
    for to in tos:
        to_str += to + ','

    infos = {'body'    : (mail_body, 'text/plain'),
             'subject' : mail_subject,
             'sender_email' : sender_email,
             'to'           : to_str[:len(to_str)-1]}

    subtool = context.portal_subscriptions
    cerror = subtool.sendmail(infos=infos)
    psm = 'psm_an_email_has_been_sent'
    redirect_url = REQUEST['URL1'] + '?portal_status_message=%s' %psm
    return REQUEST.RESPONSE.redirect(redirect_url)

##parameters=
#$Id$
""" Mail Template

XXX do sthg else than that -> body rendered with DTML
"""

mail_subject = '[Notification] %(notification_title)s for object %(object_title)s'
mail_body = \
"""%(object_type)s has created a %(notification_title)s notification.

Additional info:
User name: %(user_name)s (%(user_id)s)
Event type: %(event)s
URL: %(object_url)s
"""

mail_error_body = \
"""An error occurs while computing the body of the email.

Please contact, the administrator of the portal.
"""

template = {}
template['mail_subject'] = mail_subject
template['mail_body'] = mail_body
template['mail_error_body'] = mail_error_body

return template

##parameters=infos
#$Id$
""" Mail Template

XXX do sthg else than that -> body rendered with DTML
"""

mail_subject = '[Notification] %(notification_title)s for object %(object_title)s' %infos
mail_body = \
"""%(object_type)s has created a %(notification_title)s notification.

Additional info:
User name: %(user_name)s (%(user_id)s)
Event type: %(event)s
URL: %(object_url)s
""" %infos

template = {}
template['mail_subject'] = mail_subject
template['mail_body'] = mail_body

return template

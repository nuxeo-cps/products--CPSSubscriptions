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

subscribe_confirm_email_title = \
"""[%(portal_title)s] Confirm Subscription
"""
subscribe_confirm_email_body = \
"""Mailing list subscription confirmation notice for mailing list
%(event_id)s

We have received a request for subscription of your email
address, %(email)s, to the %(event_id)s mailing list.

To confirm that you want to be added to this mailing list, visit this web page:

%(object_url)s
"""

subscribe_welcome_email_title = \
"""[%(portal_title)s] Welcome to the mailing list at %(object_title)s
"""

subscribe_welcome_email_body = \
"""Welcome to the %(event_id)s mailing lists at

%(object_url)s

General information about the mailing list is at

%(info_url)s

If you ever want to unsubscribe or change your options, visit your subscription page at:

%(info_url)s
"""

unsubscribe_email_title = \
"""[%(portal_title)s] Unsubscription
"""

unsubscribe_email_body = \
"""You have been unsubscribed from the mailing list at %(object_title)s at %(object_url)s
"""

unsubscribe_confirm_email_title = \
"""[%(portal_title)s] Confirm  unsubscription
"""

unsubscribe_confirm_email_body = \
"""You requested to unsubscribe to the mailing list :

%(object_title)s at :

%(object_url)s

Follow the link below to confirm :

%(url)s
"""

template = {}
template['mail_subject'] = mail_subject
template['mail_body'] = mail_body
template['mail_error_body'] = mail_error_body
template['subscribe_confirm_email_title'] = subscribe_confirm_email_title
template['subscribe_confirm_email_body'] = subscribe_confirm_email_body
template['subscribe_welcome_email_title'] = subscribe_welcome_email_title
template['subscribe_welcome_email_body'] = subscribe_welcome_email_body
template['unsubscribe_email_title'] = unsubscribe_email_title
template['unsubscribe_email_body'] = unsubscribe_email_body
template['unsubscribe_confirm_email_title'] = unsubscribe_confirm_email_title
template['unsubscribe_confirm_email_body'] = unsubscribe_confirm_email_body

return template

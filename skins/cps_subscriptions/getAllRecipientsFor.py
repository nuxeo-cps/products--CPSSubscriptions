##parameters=event_type=None
#$Id$
""" Returns all the recipients in the context.

if event_type is present within the request then it returns
only the recipients for this given event type. If not
all the recipients for all the events are returned.
"""

from zLOG import LOG, DEBUG

portal_subscriptions = context.portal_subscriptions
events = context.getEventTypesFromContext()
recipients = {}
for event in events.keys():
    recipients_mails = portal_subscriptions.getRecipientsFor(event, context)
    for recipient_mail in recipients_mails.keys():
        recipients[recipient_mail] = recipients_mails[recipient_mail]
return recipients

##parameters=file=None, event_id='', REQUEST=None
"""Edit the subscription parameters

$Id$
"""

import re

subtool = context.portal_subscriptions
subscription_container = subtool.getSubscriptionContainerFromContext(context)
event = subscription_container.getSubscriptionById(event_id)
recipients_rule = event.getRecipientsRules(recipients_rule_type='Explicit Recipients Rule')[0]

stripped = [x.strip() for x in file.readlines()]

# XXX check if the mails are correct
emails = stripped
recipients_rule.importEmailsSubscriberList(emails)

if REQUEST is not None:
    redirect_url = REQUEST['URL1'] + \
                   '/folder_notifications_form' + \
                   '?portal_status_message=psm_subscription_updated'
    REQUEST.RESPONSE.redirect(redirect_url)

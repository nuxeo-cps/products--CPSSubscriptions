##parameters=REQUEST
#$Id$
""" Edit the explicit subscription configuration.

It applies for a given event. The event_id is within the REQUEST.
"""

from zLOG import LOG, DEBUG

if REQUEST is not None:
    if REQUEST.form:

        #
        # Checking if there's a local subscription container
        #

        subscription_id = context.portal_subscriptions.getSubscriptionId()
        if subscription_id not in context.objectIds():
            context.manage_addProduct[
                'CPSSubscriptions'].addSubscriptionContainer()
        subscription_folder = getattr(context, subscription_id)

        #
        # Checking the given request event
        #

        event_id = REQUEST.form.get('event_id', None)
        if not hasattr(subscription_folder, event_id):
            subscription_folder.manage_addProduct[
                'CPSSubscriptions'].addSubscription(id=event_id)

        #
        # Checking the explicit recipients rules
        #

        event = getattr(subscription_folder, event_id)
        explicit_recipients_rule_id = context.portal_subscriptions.getExplicitRecipientsRuleId()
        if not hasattr(event, explicit_recipients_rule_id):
            event.manage_addProduct[
                'CPSSubscriptions'].addExplicitRecipientsRule()

        explicit_recipients_rule = getattr(event, explicit_recipients_rule_id)
        explicit_emails = REQUEST.form.get('explicit_emails', [])
        explicit_recipients_rule.updateEmails(explicit_emails)


        black_list = REQUEST.form.get('black_list', [])
        event.updateRecipientEmailsBlackList(black_list)

return REQUEST.RESPONSE.redirect("%s/%s?portal_status_message=%s" %(context.absolute_url(),
                                                                    'folder_notifications_form',
                                                                    'psm_notifications_changed'))

##parameters=REQUEST
#$Id$
""" User subscribe to given event coming in the REQUEST

The subscptions container should be already in here since the guy got the action.
"""

from zLOG import LOG, DEBUG

if REQUEST is not None:
    if REQUEST.form:

        # @www
        email = REQUEST.form.get('subscriber_email', None)
        event_ids = REQUEST.form.get('event_ids', None)


        # Checking the requested events
        for event_id in event_ids:
            if not hasattr(subscription_folder, event_id):
                subscription_folder.manage_addProduct[
                    'CPSSubscriptions'].addSubscription(id=event_id)

        #
        # Checking the explicit recipients rules
        #

        for event_id in event_ids:
            event = getattr(subscription_folder, event_id)
            explicit_recipients_rule_id = context.portal_subscriptions.getExplicitRecipientsRuleId()
            if not hasattr(event, explicit_recipients_rule_id):
                event.manage_addProduct[
                    'CPSSubscriptions'].addExplicitRecipientsRule()

            # Default -> mail notification
            if not hasattr(event, context.portal_subscriptions.getMailNotificationRuleObjectId()):
                event.manage_addProduct[
                    'CPSSubscriptions'].addMailNotificationRule()

            explicit_recipients_rule = getattr(event, explicit_recipients_rule_id)
            if explicit_recipients_rule.updatePendingEmails(email):
                psm = 'psm_subscription_taken_into_consideration'
            else:
                psm = 'psm_subscription_not_taken_into_consideration'

return REQUEST.RESPONSE.redirect("%s/%s?portal_status_message=%s" %(context.absolute_url(),
                                                                    'folder_subscribe_form',
                                                                    psm))

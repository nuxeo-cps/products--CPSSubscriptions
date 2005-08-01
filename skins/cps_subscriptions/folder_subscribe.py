##parameters=REQUEST
#$Id$
""" User subscribe to given event coming in the REQUEST

The subscptions container should be already in here since the guy got the action.
"""

isAno = context.portal_membership.isAnonymousUser()

if REQUEST is not None:
    if REQUEST.form:
        psm = "psm_please_choose_at_least_one_event_for subscription"
        # @www
        email = REQUEST.form.get('subscriber_email', None)
        event_ids = REQUEST.form.get('event_ids',  [])
        subscriptions_tool = context.portal_subscriptions
        subscription_folder = subscriptions_tool.getSubscriptionContainerFromContext(context)
        explicit_recipients_rule_id = context.portal_subscriptions.getExplicitRecipientsRuleId()
        for event_id in event_ids:
            internal_event_id = 'subscription__'+event_id
            event = getattr(subscription_folder, internal_event_id, None)
            if event is None:
                subscription_folder.addSubscription(internal_event_id)
                event = getattr(subscription_folder, internal_event_id)
            explicit_recipients_rule = getattr(event, explicit_recipients_rule_id)
            stupid = 1
            if not explicit_recipients_rule.subscribeTo(email, event_id, context):
                stupid = 0
            if stupid:
                psm = 'psm_email_sent_to_you'
            else:
                psm = 'psm_subscription_not_taken_into_consideration'

        return REQUEST.RESPONSE.redirect("%s/%s?portal_status_message=%s&email=%s" %(context.absolute_url(),
                                                                             'folder_subscribe_form',
                                                                             psm,
                                                                             email))

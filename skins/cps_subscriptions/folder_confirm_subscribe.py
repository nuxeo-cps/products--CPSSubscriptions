##parameters=email='', event_id=''
#$Id$
"""Confirm the subscription.

Check if the confirmation can be done and then add this email to the mailing
list
"""

if not email and event_id:
    if context.REQUEST is not None:
        psm = 'psm_you_need_to_subscribe_before_trying_to_confirm'
        context.REQUEST.RESPONSE.redirect(context.absolute_url()+'?psm=%s' \
                                          %(psm))
else:
    # XXX -> move this code to subscriptions tool
    subscriptions_tool = context.portal_subscriptions
    container_id = subscriptions_tool.getSubscriptionContainerId()
    explicit_sub_id = subscriptions_tool.getExplicitRecipientsRuleId()
    subscriptions_folder = getattr(context, container_id)
    event_subscription = getattr(subscriptions_folder, 'subscription__'+event_id)
    explicit_subscriptions = getattr(event_subscription, explicit_sub_id)
    explicit_subscriptions.anonymousConfirmSubscribe(email, event_id, context)
    if context.REQUEST is not None:
        psm = 'psm_welcome_to_mailing_list'
        context.REQUEST.RESPONSE.redirect(context.absolute_url() + \
                                          '/folder_subscription_welcome?psm=%s' \
                                          %(psm))

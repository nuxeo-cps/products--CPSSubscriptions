##parameters=email='', event_id=''
#$Id$
"""Confirm the unsubscription.

Check if the confirmation can be done and then do the hob.
"""

if not email and event_id:
    if context.REQUEST is not None:
        psm = 'psm_you_need_to_subscribe_before_trying_to_confirm'
        context.REQUEST.RESPONSE.redirect(context.absolute_url()+'?psm=%s' \
                                          %(psm))
else:
    # XXX -> move this code to subscriptions tool
    subscriptions_tool = context.portal_subscriptions
    explicit_sub_id = subscriptions_tool.getExplicitRecipientsRuleId()
    subscriptions_folder = subscriptions_tool.getSubscriptionContainerFromContext(context)
    event_subscription = getattr(subscriptions_folder, 'subscription__'+event_id)
    explicit_subscriptions = getattr(event_subscription, explicit_sub_id)
    explicit_subscriptions.confirmUnSubscribeTo(email, event_id, context)
    if context.REQUEST is not None:
        psm = 'psm_you_are_removed_from_the_mailing_list'
        context.REQUEST.RESPONSE.redirect(context.absolute_url() + \
                                          '/folder_unsubscribe_form?portal_status_message=%s&email=%s' \
                                          %(psm, email))

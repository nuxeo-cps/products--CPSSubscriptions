##parameters=event_type, role
""" Is the role subscribed

We gonna check if the role is subscribed in the context.
"""

portal_subscriptions = context.portal_subscriptions
subscriptions = portal_subscriptions.getSubscriptionsFor(event_type, context, infos={})
for subscription in subscriptions:
    subscription_recipients_rule = subscription.getRecipientsRules()
    subscription_recipients_rule = [
        x for x in subscription_recipients_rule if hasattr(x, 'getRoles')]
    for recipients_rule in subscription_recipients_rule:
        if role in recipients_rule.getRoles():
            return 1
return 0

##parameters=subscription_mode=''
"""Schedule messages according to a subscriptions mode

i.e : daily / weekly / monthly
Launch that with a crond / wget or similar :

wget -q http://manager:pwd_manager@cps.foo/cps_subscriptions_schedule_notifications?subscription_mode=weekly
"""

subscriptions_tool = context.portal_subscriptions

if subscription_mode:
    if subscription_mode in  ['daily', 'weekly', 'monthly']:
        return subscriptions_tool.scheduleMessages(subscription_mode)

# subscription_mode doesn't exist or not specified
return -1

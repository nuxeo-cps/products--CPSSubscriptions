##parameters=REQUEST
#$Id$
""" Edit the local subscriptions configuration.
"""


if REQUEST:
    subscription_id = context.portal_subscriptions.getSubscriptionId()
    if not subscription_id in context.objectIds():
        context.manage_addProduct['CPSSubscriptions'].addSubscription()

    if REQUEST.form:
        role_event = REQUEST.form.get('role_event', [])

            role_event = [role_event]

    return role_event

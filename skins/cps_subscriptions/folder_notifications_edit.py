##parameters=REQUEST
#$Id$
""" Edit the local subscriptions configuration.
"""

from zLOG import LOG, DEBUG

if REQUEST is not None:
    if REQUEST.form:
        subscription_id = context.portal_subscriptions.getSubscriptionId()

        #
        # Full Update
        #

        if subscription_id in context.objectIds():
            LOG("Deleteting the subscription Folder", DEBUG, subscription_id)
            context.manage_delObjects([subscription_id])
        context.manage_addProduct[
            'CPSSubscriptions'].addPlaceFullSubscriptionFolder()

        subscription_folder = getattr(context, subscription_id)

        #
        # Subscription Folder parameters
        #

        kw = {}
        kw['notify_local_only'] = REQUEST.form.get('notify_local_only', 0) and 1
        kw['notify_no_local'] = REQUEST.form.get('notify_no_local', 0) and 1
        LOG("KWKWKKWKWKWKKWKWK", DEBUG, 'XXXX'+str(kw))
        subscription_folder.updateProperties(**kw)

        #
        # Let's take the event/roles the user request for change
        #

        role_events = REQUEST.form.get('role_event', [])
        LOG("REQUEST", DEBUG, role_events)

        for role_event in role_events:
            role = role_event.split(':')[0]
            event = role_event.split(':')[1]
            #
            # Is the event already subscribed ?
            # If not then we create it and set the properties
            #
            current_event_subscription = getattr(subscription_folder,
                                                 'subscription__'+event,
                                                 0)
            if not current_event_subscription:
                LOG("Creating new event subscription", DEBUG, 'subscription__'+event)
                subscription_folder.manage_addProduct[
                    'CPSSubscriptions'].addSubscription(id='subscription__'+event,
                                                        title=event)
            current_event_subscription = getattr(subscription_folder,
                                                 'subscription__'+event)
            current_event_subscription.addEventType(event)
            #
            # Then for the the given event let's check if the role is subscribed
            # already
            #
            if not getattr(current_event_subscription,
                           role+'__recipients_rule',
                           0):
                current_event_subscription.manage_addProduct[
                    'CPSSubscriptions'].addRoleRecipientsRule(id=role+'__recipients_rule',
                                                              title=role,
                                                              **{'roles':[role]})

return REQUEST.RESPONSE.redirect("%s/%s?portal_status_message=%s" %(context.absolute_url(),
                                                                    'folder_notifications_form',
                                                                    'psm_notifications_changed'))

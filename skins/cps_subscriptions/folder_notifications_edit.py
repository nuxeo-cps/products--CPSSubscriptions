##parameters=REQUEST
#$Id$
""" Edit the local subscriptions configuration.

The ones with the ManageSubscriptions permission can do it
"""

from zLOG import LOG, DEBUG

if REQUEST is not None:
    if REQUEST.form:
        subtool = context.portal_subscriptions

        # Checking if we have here a placefull subscription container
        subscription_id = subtool.getSubscriptionContainerId()
        if subscription_id not in context.objectIds():
            context.manage_addProduct['CPSSubscriptions'].addSubscriptionContainer()

        subscription_folder = getattr(context, subscription_id)

        # @www
        kw = {}
        kw['notify_local_only'] = REQUEST.form.get(
            'notify_local_only', 0) and 1
        kw['notify_no_local'] = REQUEST.form.get(
            'notify_no_local', 0) and 1
        kw['subscription_allowed'] = REQUEST.form.get(
            'subscription_allowed', 0) and 1
        kw['unsubscription_allowed'] = REQUEST.form.get(
            'unsubscription_allowed', 0) and 1
        kw['anonymous_subscription_allowed'] = REQUEST.form.get(
            'anonymous_subscription_allowed', 0) and 1
        kw['mfrom'] = REQUEST.form.get('mfrom', '')

        # Update properties
        subscription_folder.updateProperties(**kw)

        # Let's take the event/roles the user request for change
        role_events = REQUEST.form.get('role_event', [])

        # Cleaning / reinit
        for subscription_id in subscription_folder.objectIds():
            ob = getattr(subscription_folder,
                         subscription_id)
            to_delete = [x for x in ob.objectValues() if
                         x.meta_type == 'Role Recipient Rule']
            to_delete =  [x.id for x in to_delete if x not in [
                y.split(':')[0] for y in role_events]]
            try:
                ob.manage_delObjects(to_delete)
            except:
                pass

        # Updating
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
            # Default -> mail notification
            if not hasattr(current_event_subscription,
                           context.portal_subscriptions.getMailNotificationRuleObjectId()):
                current_event_subscription.manage_addProduct[
                    'CPSSubscriptions'].addMailNotificationRule()
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

        # Dunno if I should ?
        subscription_folder.reindexObject(idxs=['portal_type', 'getSubscriptions'])
return REQUEST.RESPONSE.redirect("%s/%s?portal_status_message=%s" %(context.absolute_url(),
                                                                    'folder_notifications_form',
                                                                    'psm_notifications_changed'))

##parameters=REQUEST
#$Id$
""" Edit the local subscriptions configuration.

Manager / WorkspaceManager / SectionManager can do that.
"""

# XXX use the tool methods to get prefixes and constantes for ids.

from zLOG import LOG, DEBUG

if REQUEST is not None:
    if REQUEST.form:
        subscription_id = context.portal_subscriptions.getSubscriptionContainerId()
        if subscription_id not in context.objectIds():
            context.manage_addProduct['CPSSubscriptions'].addSubscriptionContainer()

        subscription_folder = getattr(context, subscription_id)

        # @www
        kw = {}
        kw['notify_local_only'] = REQUEST.form.get('notify_local_only', 0) and 1
        kw['notify_no_local'] = REQUEST.form.get('notify_no_local', 0) and 1
        kw['subscription_allowed'] = REQUEST.form.get('subscription_allowed', 0) and 1
        kw['unsubscription_allowed'] = REQUEST.form.get('unsubscription_allowed', 0) and 1
        kw['anonymous_subscription_allowed'] = REQUEST.form.get('anonymous_subscription_allowed', 0) and 1
        kw['mfrom'] = REQUEST.form.get('mfrom', '')

        subscription_folder.updateProperties(**kw)

        # Let's take the event/roles the user request for change
        role_events = REQUEST.form.get('role_event', [])
        LOG("REQUEST", DEBUG, role_events)

        # Cleaning unwanted ones
        all_requested_subscription = ['subscription__'+x.split(':')[1] for x in role_events]
        for subscription_id in subscription_folder.objectIds():
            current_event_subscription = getattr(subscription_folder,
                                                 subscription_id)
            if subscription_id not in all_requested_subscription:
                if 'explicit__recipients_rule' not in current_event_subscription.objectIds():
                    subscription_folder.manage_delObjects([subscription_id])
            else:
                for event in current_event_subscription.objectIds():
                    requested_role_for_subscriptions = [x.split(':')[0]+'__recipients_rule'  \
                                                        for x in role_events if x.split(':')[1] == event]
                    if event not in requested_role_for_subscriptions and not event.startswith('explicit') and \
                       not event.startswith('explicit'):
                        current_event_subscription.manage_delObjects([event])

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

##parameters=REQUEST
#$Id$
""" User unsubscribe to given event coming in the REQUEST

The subscptions container should be already in here since the guy got the action.
"""

isAno = context.portal_membership.isAnonymousUser()
if not isAno:
    member = context.portal_membership.getAuthenticatedMember()
    member_id = member.getMemberId()
    member_email = context.getMemberEmail(member_id)

if REQUEST is not None:
    if REQUEST.form:
        psm = "psm_please_choose_at_least_one_event_for unsubscription"
        # @www
        event_ids = REQUEST.form.get('event_ids',  [])
        subscriptions_tool = context.portal_subscriptions
        subscription_folder = subscriptions_tool.getSubscriptionContainerFromContext(context)
        for event_id in event_ids:
            internal_event_id = 'subscription__'+event_id
            event = getattr(subscription_folder, internal_event_id)
            for recipients_rule in event.getRecipientsRules(recipients_rule_type='Role Recipient Rule'):
                if member_email in recipients_rule.getRecipients(event_id, object=context).keys():
                    recipients_rule.addUnSubscribedMember(member_id)
        
        psm = "psm_you_have_been_removed_from_the_list_contact_the_administrator_if_needed"
            
    return REQUEST.RESPONSE.redirect("%s/%s?portal_status_message=%s" %(context.absolute_url(),
                                                                             'folder_subscribe_form',
                                                                             psm))

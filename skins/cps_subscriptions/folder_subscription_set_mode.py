##parameters=REQUEST=None
"""Set the subscription mode for a given email
"""

if REQUEST is not None:
    if REQUEST.form:
        form = REQUEST.form
        email = form.get('email')
        mode  = form.get('subscription_mode')
        if email and mode:
            # Changing the mode
            subscriptions_tool = context.portal_subscriptions
            subscription_folder = subscriptions_tool.getSubscriptionContainerFromContext(context)
            subscription_folder.updateUserMode(email, mode)

            # Redirection
            psm = 'psm_user_mode_updated'
            return REQUEST.RESPONSE.redirect("%s/%s?portal_status_message=%s" %(context.absolute_url(),
                                                                                'folder_subscribe_form',
                                                                                psm))

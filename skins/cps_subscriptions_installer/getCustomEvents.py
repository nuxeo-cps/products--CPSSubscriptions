##parameters=
#$Id$
""" Returns the custom Subscriptions events

Use by the installer at setup/update time.
Check the getEvents syntax and override this file within your product.
The dict key is the portal type of the container where
you'd like to be able to get notifications features.
*IMPORTANT* if you define a new dict key the default ones will be override.
"""
###################################

events = {}

return events

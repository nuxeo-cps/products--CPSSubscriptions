##parameters=member_id
#$Id$
""" Returns the mail of a given user

This script will be usefull in custom member directories such as LDAP
while using the CPSDirectory with different schemas as the default
CPS ones.
"""

if member_id:
    membership = context.portal_membership
    return membership.getEmailFromUsername(member_id)

return None

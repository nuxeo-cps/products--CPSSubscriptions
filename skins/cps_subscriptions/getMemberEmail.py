##parameters=member_id
#$Id$
""" Returns the mail of a given user

This script will be usefull in custom member directories such as LDAP
while using the CPSDirectory with different schemas as the default
CPS ones.
"""

if member_id:
    mtool = context.portal_membership
    member = mtool.getMemberById(member_id)
    return member.getProperty('email')
return None

##parameters=
#$Id$
""" Returns the CPS Subscriptions events

Use by the installer.  The dict key is the portal type of the container where
you'd like to be able to get notifications features.
"""

dict = {}

workspace = {'workflow_create' : 'label_creation_of_documents',
             'workflow_modify' : 'label_modification_of_documents',
             'workflow_cut_copy_paste' : 'label_cut_copy_paste_of_documents',
             }

###################################

dict['Workspace'] = workspace
dict['Portal'] = workspace
#
# Custom events
#

custom = context.getCustomEvents()

for key in custom.keys():
    dict[key] = custom[key]

return dict

##parameters=
#$Id$
""" Returns the CPS Subscriptions events

Use by the installer.  The dict key is the portal type of the container where
you'd like to be able to get notifications features.

The key is the portal_type of the containers.
"""

dict = {}

workspace = {'workflow_create' : 'label_creation_of_documents',
             'workflow_modify' : 'label_modification_of_documents',
             'workflow_cut_copy_paste' : 'label_cut_copy_paste_of_documents',
             }

section = {'workflow_publish' : 'label_publication_of_documents',
           'workflow_modify' : 'label_modification_of_documents',
           'workfow_submit'  : 'label_submission_of_documents',
           'workflow_cut_copy_paste' : 'label_cut_copy_paste_of_documents',
           'workflowr_reject' : 'label_rejecttion_of_documents',
           'workflow_unpublish' : 'label_unpublication_of_documents',
           }

###################################

dict['Workspace'] = workspace
dict['Section'] = section
dict['Portal'] = workspace   # Has to disappear soon.


# Custom events (Projects eventually)
custom = context.getCustomEvents()

for key in custom.keys():
    dict[key] = custom[key]

return dict

##parameters=
#$Id$
""" Returns the CPS Subscriptions events

Use by the installer.  The dict key is the portal type of the container where
you'd like to be able to get notifications features.

The key is the portal_type of the containers.
"""

dict = {}

workspace = {'workflow_create' : 'label_workflow_create',
             'workflow_modify' : 'label_workflow_modify',
             'workflow_cut_copy_paste' : 'label_workflow_cut_copy_paste',
             }

section = {'workflow_publish' : 'label_workflow_publish',
           'workflow_accept' : 'label_workflow_accept',
           'workflow_modify' : 'label_workflow_modify',
           'workflow_submit'  : 'label_workflow_submit',
           'workflow_cut_copy_paste' : 'label_workflow_cut_copy_paste',
           'workflow_reject' : 'label_workflow_reject',
           'workflow_unpublish' : 'label_workflow_unpublish',
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

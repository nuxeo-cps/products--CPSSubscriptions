##parameters=loadcustom=1
#$Id$
""" Returns the CPS Subscriptions events

Use by the installer. The events dictionnary key is the portal type of the
container where you'd like to be able to get notifications features.

The key is the portal_type of the containers.
"""

events = {}

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

events['Workspace'] = workspace
events['Section'] = section
events['Portal'] = workspace   # Has to disappear soon.


if loadcustom:
    cevents = context.getCustomEvents()
    events.update(cevents)

return events

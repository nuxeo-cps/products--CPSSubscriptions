##parameters=
"""
Returns all the possible event types according to the context. (Workspace/Sections in CPS)
Override this one if needed.
"""

workspaces_alert_types = {'workflow_create' : 'label_creation_of_documents',
                          'workflow_modify' : 'label_modification_of_documents',
                          'workflow_cut_copy_paste' : 'label_cut_copy_paste_of_documents',
                          }

if context.portal_type == 'Workspace':
    return workspaces_alert_types
elif context.portal_type == 'Section':
    raise('No alert types available within an object of type : %s'
          %(context.portal_type))
else:
    raise('No alert types available within an object of type : %s'
          %(context.portal_type))

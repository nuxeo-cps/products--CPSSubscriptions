##parameters=
"""
Returns the local roles in the context. (Workspace/Section for CPS)
Override this one in your owan application if you defined new roles.
"""

workspaces_local_roles = {'WorkspaceManager': 'label_workspace_manager',
                          'WorkspaceMember' : 'label_workspace_member',
                          'WorkspaceReader' : 'label_workspace_reader',
                          }
sections_local_roles = {'SectionManager'  : 'label_section_manager',
                        'SectionReviewer' : 'label_section_reviewer',
                        'SectionReader'   : 'label_section_reader',
                        }

if context.portal_type == 'Workspace':
    return workspaces_local_roles
elif context.portal_type == 'Section':
    return sections_local_roles
else:
    raise('Subscriptions not implemented for : %s' %(context.portal_type))

##parameters=loadcustom=1
#$Id$
"""
Returns the local roles in the context. (Workspace/Section for CPS)
Override this one in your owan application if you defined new roles.
"""

# Workspace
workspaces_local_roles = {'WorkspaceManager': 'label_workspace_manager',
                          'WorkspaceMember' : 'label_workspace_member',
                          'WorkspaceReader' : 'label_workspace_reader',
                          'Owner'           : 'label_owner',
                          'Manager'         : 'label_manager',
                          }
# Section
sections_local_roles = {'SectionManager'  : 'label_section_manager',
                        'SectionReviewer' : 'label_section_reviewer',
                        'SectionReader'   : 'label_section_reader',
                        'Owner'           : 'label_owner',
                        'Manager'         : 'label_manager',
                        }
# Forum
forum_local_roles_sections = {'Owner' : 'label_owner',
                              'ForumPoster':'label_forum_poster',
                              'ForumModerator':'label_forum_moderator',
                              'SectionManager'  : 'label_section_manager',
                              'SectionReviewer' : 'label_section_reviewer',
                              'SectionReader'   : 'label_section_reader'}

forum_local_roles_workspaces = {'Owner' : 'label_owner',
                                'ForumPoster':'label_forum_poster',
                                'ForumModerator':'label_forum_moderator',
                                'WorkspaceManager': 'label_workspace_manager',
                                'WorkspaceMember' : 'label_workspace_member',
                                'WorkspaceReader' : 'label_workspace_reader'}

if context.portal_type == 'Workspace':
    return workspaces_local_roles
elif context.portal_type == 'Section':
    return sections_local_roles

# Forum
elif context.portal_type == 'CPSForum':
    if context.aq_inner.aq_parent.portal_type == 'Section':
        return forum_local_roles_sections
    else:
        return forum_local_roles_workspaces
elif context.portal_type == 'ForumPost':
    if (context.aq_inner.aq_parent).aq_inner.aq_parent.portal_type == 'Section':
        return forum_local_roles_sections
    else:
        return forum_local_roles_workspaces
else:
    raise('Subscriptions not implemented for : %s' %(context.portal_type))

##parameters=loadcustom=1
#$Id$
"""
Returns the local role areas / subscription contexts / relevant local roles
Default values for the first installation

You may use the API of the SubscriptionsTool to custiomize these values.

Don't override this skins if you wanna avoid update problems. Be real, use the API.
"""

mapping = {'Workspace' : {'Workspace': {'WorkspaceManager': 'label_workspace_manager',
                                        'WorkspaceMember' : 'label_workspace_member',
                                        'WorkspaceReader' : 'label_workspace_reader',
                                        'Owner'           : 'label_owner',
                                        },
                          'CPSForum' : {'Owner' : 'label_owner',
                                        'ForumPoster':'label_forum_poster',
                                        'ForumModerator':'label_forum_moderator',
                                        'WorkspaceManager': 'label_workspace_manager',
                                        'WorkspaceMember' : 'label_workspace_member',
                                        'WorkspaceReader' : 'label_workspace_reader'}
                          },
           'Section' :  {'Section' : {'SectionManager'  : 'label_section_manager',
                                      'SectionReviewer' : 'label_section_reviewer',
                                      'SectionReader'   : 'label_section_reader',
                                      'Owner'           : 'label_owner',
                                      },
                         'CPSForum' : {'Owner' : 'label_owner',
                                       'ForumPoster':'label_forum_poster',
                                       'ForumModerator':'label_forum_moderator',
                                       'SectionManager'  : 'label_section_manager',
                                       'SectionReviewer' : 'label_section_reviewer',
                                       'SectionReader'   : 'label_section_reader'},
                         },
           }
return mapping

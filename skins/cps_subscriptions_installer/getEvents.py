##parameters=loadcustom=1
#$Id$
""" Returns the CPS Subscriptions events

This script is used by the CPSSubscriptions installer.

The events dictionary key is the portal type of the container where you'd like
to be able to get notifications features.

Then each container is in turn a dictionary which keys are the transition names
of their workflow suffixed with the 'workflow_' string.
"""

events = {}

workspace = {'workflow_create' : 'label_workflow_create',
             'workflow_modify' : 'label_workflow_modify',
             'workflow_delete' : 'label_workflow_delete',
             'workflow_cut_copy_paste' : 'label_workflow_cut_copy_paste',
             'forum_new_comment' : 'label_forum_new_comment',
             'forum_comment_published' : 'label_forum_comment_published',
             'forum_comment_unpublished' : 'label_forum_comment_unpublished',
             'forum_comment_rejected' : 'label_forum_comment_rejected',
             'forum_comment_deleted' : 'label_forum_comment_deleted',}

section = {'workflow_publish' : 'label_workflow_publish',
           'workflow_accept' : 'label_workflow_accept',
           'workflow_modify' : 'label_workflow_modify',
           'workflow_delete' : 'label_workflow_delete',
           'workflow_submit'  : 'label_workflow_submit',
           'workflow_cut_copy_paste' : 'label_workflow_cut_copy_paste',
           'workflow_reject' : 'label_workflow_reject',
           'workflow_unpublish' : 'label_workflow_unpublish',
           }

cps_forum = {'forum_new_post' : 'label_forum_new_post',
             'forum_post_published' : 'label_forum_post_published',
             'forum_post_unpublished' : 'label_forum_post_unpublished',
             'forum_post_rejected' : 'label_forum_post_rejected',
             'forum_post_deleted' : 'label_forum_post_deleted',
             }


cps_forum_post = {'forum_new_post' : 'label_forum_new_post',
                  'forum_post_published' : 'label_forum_post_published',}

###################################

events['Workspace'] = workspace
events['Section'] = section
events['CPSForum'] = cps_forum
events['ForumPost'] = cps_forum_post

if loadcustom:
    cevents = context.getCustomEvents()
    events.update(cevents)

return events

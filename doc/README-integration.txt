============================================================
CPSSubscriptions -- Integration on projects and cutomization
============================================================


:Revision: $Id$

.. sectnum::    :depth: 4
.. contents::   :depth: 4

  

*Note:* It's working with a default configuration in state. The following
id useful when you have custom workflows or new containers.

Registration
============


- Registering new events in given contexts

  Add a getCustomEvents.py file within your skins directory if you
  want to record new events and /or new contexts where you want
  notifications to be in use.

  (See getEvents.py in CPSSubscriptiosn skins for the syntax.)

- Registering new local roles

  If you're using different local roles than the default CPS ones
  you may do the following :

  Add a getLocalRolesFromContext.py within your skins directory.

  (See getLocalRolesFromContent in CPSSubscriptions skins for the
  syntax.)


Content of sent messages.
=========================

Define a getMailTemplate.py files within your skins directory
based on the getMailTemplate.py included within the
CPSSubsriptions skins.

You will be able to edit message content.

Below, is the list of variables you may use in the messages by
using the following syntax: ``%(variable_name)s``.

- portal_title : Title of the portal

- info_url : URL of the page summarizing the subscription
  informations

- notification_title : Title of the notification

- event : Id of the event

- object_title : Tiltle of the object generating the notification

- object_url   : URL of the object generating the notification

- object_parent_title : Parent object Title

- object_type : portal_type of the object generating the
  notifications

- object_creator_id : Id of the user who created the object on
  which the event occured

- object_creator_name : Fullname of the user who created the
  object on which the event occured

- user_id : Id of the user who provided an action that generated
  the notification.

- user_name : Fullname of the user who provided an action that
  generated the notification.

- comments : Comments which where given by the user when she asks
  for a workflow transition.

- kwargs_xxx : Specific information from workflows. Warning :
  those variables can only be used for event messages coming from
  workflows, otherwise it will generate errors.

- All the field values of schemas for FlexibleTypeInformation and
  all attributes for 'normal' zope objects


Customization of given notification event messages
==================================================

Through the ZMI you may edit the content of messages.

- Global message content

- Event specific message content


.. Emacs
.. Local Variables:
.. mode: rst
.. End:
.. Vim
.. vim: set filetype=rst:


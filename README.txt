                           CPSSubscriptions

                  Event subscriptions and notifications

                                  ---

  $Id$


  This component provides subscriptions and notifications for CPS3.

Definition:

  - Subscription

    A subscription, within CPSSubscriptions, can be seen as a mailing list
    subscription. It is usually linked to a given event and portal members
    or visitors can be notified when this given event occurs by either
    subscribing or either having roles which are setup to notify on these
    given events by a manager. Or still being part explicitly of the mailing
    list. (Manager can add email explicitly)

  - Notifications

    CPSSubscriptions can right now handle mail notifications but it could be
    extended to SMS, Jabber or whatever notifications thanks the
    architecture modularity.

Features:

  1 - Placeful notification management.

    Person granted with the 'ManageSubscriptions' permissions (Manage,
    WorkspaceManager, SectionManager, ...) can set recipients rules based on
    roles on folders such as Workspaces, Sections, Forums, etc.

    They have a new action 'Notifications management' available where they
    are granted with 'ManageSubscriptions' privileges. A dedicated
    management form is then provided to them where they can do the following:

      - Say who is going to be notified when a given event occur in
        here. Such as "I want the WorkspaceMembers" being notified when a
        new document is created in this workspace" or "I want the
        SectionReviewer being notified when a document has been published in
        this section" or still "I want the posters being notified when a
        reply has been done on one of their personal posts" etc. Notice,
        the use cases can be easily extended to some more complex cases.

      - Can open or close a given event for a Member or Anonymous
        subscription

      - Can add explicit persons to a given event to be notified

         - Adding explicit emails
         - Adding explicit members
         - Adding explicit groups

      - Can put some emails in a black lists for a given event.

      - Configuration options

        - Notify only people having local roles in here or not.
        - Notify only events happening in sub-folders
        - Are subscription allowed ?
        - Are unsubscription allowed for members computed as recipients
          based on their roles?
        - Are anonymous subscriptions allowed ?
        - Email appearing as sender for the outgoing emails. (Default
          creator of the folder

      - Possibility of seeing all the members / emails for all events.

   Basically, the mailing lists content such as the ones in CPS2 are now
   merged within the CPS3 and more particularly within containers. So no need
   with CPSSubscriptions, to create several mailing lists in a given
   folder.

   A well, the settings for a subscription is placeful. It means, that
   the settings are in use in the sub-folders but they can be overrides too
   the same way by performing a notification management on a sub-folders.

   To sum up: CPSSubscriptions provides now integrated mailing lists on
   containers. (See 4 - Notifications administrative management through ZMI
   for more information about configuration)

  2 - Members / Portal visitors subscriptions

      An action on the portal, folder action, 'I subscribe' permits members
      / Anonymous to subscribe to event opened for subscriptions.

     a) Members subscriptions

        If a folder is open for subscriptions then members can request for
        subscriptions.

        He chooses in the list of events which one he is interested in and
        submits.

        Either, the subscription will be taken into consideration straight
        forward either a confirmation email will be sent and the member will
        have to follow a link and confirm the subscription.

     b) Anonymous Subscriptions

        If a folder is opened for anonymous subscriptions then an anonymous
        can request for subscriptions.

        He has to choose the event he is interested in and then submit.
        Always, he will have to confirm the subscription. A confirmation
        email is sent to him providing a confirmation link on the portal.

        A given email cannot be spawn more than once since the requested
        emails are kept so that you can't request more than once for a given
        address.

  3 - Managing subscriptions as a member of the portal

    CPSSubscriptions provides the possibility for a member to manage all the
    subscriptions he belongs to everywhere within the portal through a single
    action.

    He can access this, by following the action 'My subscriptions' on the
    portal appearing within the user actions.

    An interface will show him all the subscriptions he belongs to and where
    they are located on the portal. Thus, the member, can handle its
    subscriptions from a single access point.

    To summarize: CPSSubscriptions provides a subscription centralized
    management interface for the member of the portal.

  4 - Administrative management through ZMI for notifications

    a) Add new events 'somewhere' in the portal.

       You can add some subscriptable container types such as Forum, Chat or
       whatever from the subscriptions tool as Manager in the ZMI.

    b) Edit / customize sent messages on notifications and subscriptions.

       You can customize default message email content ans as well providing
       custom content for given events.

What doesn't provide CPSSubscriptions:

  - No mailing list content type as CPS2 or CPSMailingLists used to
    provide.
  - No Newsletters content type neither. (A CPSNewsLetters will handle this
    feature and will use CPSSubscriptions for sending emails.)

Installation:

 - Classic External method installation right now. Will be integrated within
   CPS3.1

More information:

   - doc sub folders. (Especially, the README.INTEGRATION)
   - doc/API sub-folder

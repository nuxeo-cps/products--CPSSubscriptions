##parameters=
## $Id$
"""
This script remove all CPS Mailing List object from your cps.

CPSMailingList is depecrated you should use CPSSubscription
and CPSNewsLetters now.

WARNING this script **ERASE** all objects with a
meta_type== MailingListDocument or NewsLetterDocument
this script will remove these type of documents from the protal_types tool
and remove portal_subscription as well

use it as your own risk

Howto use this script
 - Log into the ZMI as manager
 - Go to your CPS root directory
 - Create an External Method with the following parameters:

     id            : removeOldCPSMailingListObjects
     title         :
     Module Name   : CPSSubscriptions.removeOldCPSMailingListObjects
     Function Name : removeOldCPSMailingListObjects

 - save it
 - then click on the test tab of this external method
"""
from zLOG import LOG, INFO, DEBUG
from Products.CMFCore.utils import getToolByName
from Products.CPSInstaller.CPSInstaller import CPSInstaller

def removeOldCPSMailingListObjects(self):
    installer = CPSInstaller(self,
                             product_name="removeOldCPSMailingListObjects")

    installer.log("removeOldCPSMailingListObjects sart")
    ttool = installer.getTool('portal_types')

    ptypes = ("MailingListDocument", "NewsLetterDocument")
    for ptype in ptypes:
        installer.log("  removing %s objects" % ptype)
        items = installer.portal.portal_catalog(portal_type=ptype)
        installer.log("    found %s objects" % len(items))
        item_count = 0
        for item in items:
            item_path = item.getPath()
            parent_path = item_path.split('/')[:-1]
            item_id = item_path.split('/')[-1]
            if parent_path and item_path:
                installer.log("   remove %s" % item_path)
                # need this hack because of broken object
                parent = self.unrestrictedTraverse(parent_path)
                try:
                    parent.folder_delete(ids=[item_id])
                    item_count += 1
                except AttributeError:
                    # invalid catalog entry ?
                    pass

        installer.log("    deleted %s done" % item_count)
        if hasattr(ttool, ptype):
            installer.log("    remove portal_type %s" % ptype)
            ttool.manage_delObjects([ptype])

    if installer.portalHas('portal_subscription'):
        installer.log("  removing portal_subscription")
        installer.portal.manage_delObjects(['portal_subscription'])
    return installer.logResult()

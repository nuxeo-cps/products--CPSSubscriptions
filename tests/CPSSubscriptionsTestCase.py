from Testing import ZopeTestCase
from Products.ExternalMethod.ExternalMethod import ExternalMethod

from Products.CPSDefault.tests import CPSTestCase

ZopeTestCase.installProduct('CPSSubscriptions')

CPSSubscriptionsTestCase = CPSTestCase.CPSTestCase

class CPSSubscriptionsInstaller(CPSTestCase.CPSInstaller):
    def addPortal(self, id):
        """Override the Default addPortal method installing
        a Default CPS Site.

        Will launch the external method for CPSSubscriptions too.
        """

        # CPS Default Site
        CPSTestCase.CPSInstaller.addPortal(self, id)
        portal = getattr(self.app, id)

        # Install the CPSSubscriptions product
        if 'cpssubscriptions_installer' not in portal.objectIds():
            cpssubscriptions_installer = ExternalMethod('cpsubscriptions_installer',
                                                        '',
                                                        'CPSSubscriptions.install',
                                                        'install')
            portal._setObject('cpssubscriptions_installer', cpssubscriptions_installer)
        portal.cpssubscriptions_installer()

CPSTestCase.setupPortal(PortalInstaller=CPSSubscriptionsInstaller)


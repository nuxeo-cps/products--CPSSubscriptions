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
        factory = self.app.manage_addProduct['CPSDefault']
        factory.manage_addCPSDefaultSite(id,
                                         root_password1="passwd",
                                         root_password2="passwd",
                                         langs_list=['fr', 'en'])

        portal = getattr(self.app, id)

        # Install the CPSSubscriptions product
        cpssubscriptions_installer = ExternalMethod('cpsubscriptions_installer',
                                                    '',
                                                    'CPSSubscriptions.install',
                                                    'install')
        portal._setObject('cpssubscriptions_installer', cpssubscriptions_installer)
        portal.cpssubscriptions_installer()

CPSTestCase.setupPortal(PortalInstaller=CPSSubscriptionsInstaller)


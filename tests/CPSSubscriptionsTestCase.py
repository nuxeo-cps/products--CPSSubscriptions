from Testing import ZopeTestCase
from Products.CPSDefault.tests import CPSTestCase

ZopeTestCase.installProduct('CPSSubscriptions')

CPSTestCase.setupPortal()

CPSSubscriptionsTestCase = CPSTestCase.CPSTestCase



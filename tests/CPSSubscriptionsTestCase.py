from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSDefault.tests.CPSDefaultLayer import ExtensionProfileLayerClass


class LayerClass(ExtensionProfileLayerClass):
    extension_ids = ('CPSSubscriptions:default',)

CPSSubscriptionsLayer = LayerClass(__name__, 'CPSSubscriptionsLayer')


class CPSSubscriptionsTestCase(CPSTestCase):
    layer = CPSSubscriptionsLayer

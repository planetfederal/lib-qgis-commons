import unittest
import os
import sys

from utilities import loadTestProject
from qgiscommons.settings import setPluginSetting, pluginSetting, readSettings
from qgiscommons.layers import *
from qgis.utils import iface
from qgis.core import QgsRasterLayer, QgsVectorLayer

def _testFile(f):
    return os.path.join(os.path.dirname(__file__), 'data', f)

class TestLayers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        readSettings(_testFile('settings.json'))
        loadTestProject("raleigh")

    def testAllLayers(self):
        layers = mapLayers()
        self.assertEqual(6, len(layers))

    def testAllLayersFilteredByName(self):
        layers = mapLayers("downtown")
        self.assertEqual(3, len(layers))        

    def testLayerFromName(self):
        layers = layerFromName("Streets")
        self.assertTrue(isinstance(layer, QgsRasterLayer))
        self.assertEqual("Streets", layer.name())

    def testLayerFromNameWrongName(self):
        self.assertRaises(WrongNameException, lambda: layerFromName("wrongname"))        

    def testVectorLayers(self):
        layers = vectorLayers()
        self.assertEqual(6, len(layers))    
    
class TestLayersB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        readSettings(_testFile('settings.json'))
        
    def setUp(self):
        iface.newProject()

    def testAddRasterLayer(self):
        layer = loadLayerNoCrsDialog(_testFile("raster_raleigh.tiff"))
        self.assertTrue(isinstance(layer, QgsRasterLayer))
        addLayer(layer)
        layers = mapLayers()
        self.assertEqual(1, len(layers))
        self.assertTrue(isinstance(layers[0], QgsRasterLayer))

    def testAddVectorLayer(self):
        layer = loadLayerNoCrsDialog(_testFile("raster_downtown.shp"))
        self.assertTrue(isinstance(layer, QgsRasterLayer))
        addLayer(layer)
        layers = mapLayers()
        self.assertEqual(1, len(layers))
        self.assertTrue(isinstance(layers[0], QgsVectorLayer))        
        
def suite():
    suite = unittest.makeSuite(TestLayers, 'test')
    suite.addTests(unittest.makeSuite(TestLayersB, 'test'))
    return suite


def run_all():
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())

if __name__ == '__main__':
    unittest.main()

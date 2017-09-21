import unittest
import os
import sys

try:
    from utilities import loadTestProject
except ImportError:
    from .utilities3 import loadTestProject

from qgiscommons2.settings import setPluginSetting, pluginSetting, readSettings
from qgiscommons2.layers import *
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
        self.assertEqual(9, len(layers))

    def testAllLayersFilteredByName(self):
        layers = mapLayers("Buildings")
        self.assertEqual(1, len(layers))        

    def testLayerFromName(self):
        layer = layerFromName("Streets")
        self.assertTrue(isinstance(layer, QgsVectorLayer))
        self.assertEqual("Streets", layer.name())

    def testLayerFromNameWrongName(self):
        self.assertRaises(WrongLayerNameException, lambda: layerFromName("wrongname"))        

    def testVectorLayers(self):
        layers = vectorLayers()
        self.assertEqual(8, len(layers))    
    
class TestLayersB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        readSettings(_testFile('settings.json'))
        
    def setUp(self):
        iface.newProject()

    def testAddRasterLayer(self):
        layer = loadLayerNoCrsDialog(_testFile("raster_raleigh.tiff"), provider='gdal')
        self.assertTrue(isinstance(layer, QgsRasterLayer))
        addLayer(layer)
        layers = mapLayers()
        self.assertEqual(1, len(layers))
        self.assertTrue(isinstance(list(layers)[0], QgsRasterLayer))

    def testAddVectorLayer(self):
        layer = loadLayerNoCrsDialog(_testFile("raleigh_downtown.shp"), provider='ogr')
        self.assertTrue(isinstance(layer, QgsVectorLayer))
        addLayer(layer)
        layers = mapLayers()
        self.assertEqual(1, len(layers))
        self.assertTrue(isinstance(list(layers)[0], QgsVectorLayer))        
        
def suite():
    suite = unittest.makeSuite(TestLayers, 'test')
    suite.addTests(unittest.makeSuite(TestLayersB, 'test'))
    return suite


def run_all():
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())

if __name__ == '__main__':
    unittest.main()

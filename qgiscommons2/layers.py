import os
import re
from qgis.core import *
from PyQt4 import QtGui, QtCore

_layerreg = QgsMapLayerRegistry.instance()

def mapLayers(name=None, types=None):
    """
    Return all the loaded layers.  Filters by name (optional) first and then type (optional)
    :param name: (optional) name of layer to return..
    :param type: (optional) The QgsMapLayer type of layer to return. Accepts a single value or a list of them
    :return: List of loaded layers. If name given will return all layers with matching name.
    """
    if types is not None and not isinstance(types, list):
        types = [types]
    layers = _layerreg.mapLayers().values()
    _layers = []
    if name or types:
        if name:
            _layers = [layer for layer in layers if re.match(name, layer.name())]
        if types:
            _layers += [layer for layer in layers if layer.type() in types]
        return _layers
    else:
        return layers

def vectorLayers():
    return mapLayers(types = QgsVectorLayer.VectorLayer)

def addLayer(layer, loadInLegend=True):
    """
    Add one or several layers to the QGIS session and layer registry.
    :param layer: The layer object or list with layers  to add the QGIS layer registry and session.
    :param loadInLegend: True if this layer should be added to the legend.
    :return: The added layer
    """
    if not hasattr(layer, "__iter__"):
        layer = [layer]
    QgsMapLayerRegistry.instance().addMapLayers(layer, loadInLegend)
    return layer

TYPE_MAP = {
    str: QtCore.QVariant.String,
    float: QtCore.QVariant.Double,
    int: QtCore.QVariant.Int,
    bool: QtCore.QVariant.Bool
}

GEOM_TYPE_MAP = {
    QGis.WKBPoint: 'Point',
    QGis.WKBLineString: 'LineString',
    QGis.WKBPolygon: 'Polygon',
    QGis.WKBMultiPoint: 'MultiPoint',
    QGis.WKBMultiLineString: 'MultiLineString',
    QGis.WKBMultiPolygon: 'MultiPolygon',
}

def _toQgsField(f):
    if isinstance(f, QgsField):
        return f
    return QgsField(f[0], TYPE_MAP.get(f[1], QtCore.QVariant.String))

def _fieldName(f):
    if isinstance(f, basestring):
        return f
    return f.name()

def newPointsLayer(filename, fields, crs, encoding="utf-8"):
    return newVectorLayer(filename, fields, QGis.WKBPoint, crs, encoding)

def newLinesLayer(filename, fields, crs, encoding="utf-8"):
    return newVectorLayer(filename, fields, QGis.WKBLine, crs, encoding)

def newPolygonsLayer(filename, fields, crs, encoding="utf-8"):
    return newVectorLayer(filename, fields, QGis.WKBPolygon, crs, encoding)

def newVectorLayer(filename, fields, geometryType, crs, encoding="utf-8"):
    '''
    Creates a new vector layer

    :param filename: The filename to store the file. The extensions determines the type of file.
    If extension is not among the supported ones, a shapefile will be created and the file will 
    get an added '.shp' to its path.
    If the filename is None, a memory layer will be created

    :param fields: the fields to add to the layer. Accepts a QgsFields object or a list of tuples (field_name, field_type)
    Accepted field types are basic Python types str, float, int and bool

    :param geometryType: The type of geometry of the layer to create.

    :param crs: The crs of the layer to create. Accepts a QgsCoordinateSystem object or a string with the CRS authId.

    :param encoding: The layer encoding
    '''
    if isinstance(crs, basestring):
        crs = QgsCoordinateReferenceSystem(crs)
    if filename is None:
        uri = self.GEOM_TYPE_MAP[geometryType]
        if crs.isValid():
            uri += '?crs=' + crs.authid() + '&'
        fieldsdesc = ['field=' + f for f in fields]

        fieldsstring = '&'.join(fieldsdesc)
        uri += fieldsstring
        layer = QgsVectorLayer(uri, "mem_layer", 'memory')
    else:
        formats = QgsVectorFileWriter.supportedFiltersAndFormats()
        OGRCodes = {}
        for (key, value) in formats.items():
            extension = unicode(key)
            extension = extension[extension.find('*.') + 2:]
            extension = extension[:extension.find(' ')]
            OGRCodes[extension] = value

        extension = os.path.splitext(filename)[1][1:]
        if extension not in OGRCodes:
            extension = 'shp'
            filename = filename + '.shp'

        if isinstance(fields, QgsFields):
            qgsfields = fields
        else:
            qgsfields = QgsFields()
            for field in fields:
                qgsfields.append(_toQgsField(field))

        QgsVectorFileWriter(filename, encoding, qgsfields,
                            geometryType, crs, OGRCodes[extension])

        layer = QgsVectorLayer(filename, os.path.basename(filename), 'ogr')

    return layer


def createWmsLayer(url, layer, style, crs):
    pass

def createWfsLayer(url, layer, crs):
    pass

class WrongLayerNameException(BaseException) :
    pass

class WrongLayerSourceException(BaseException) :
    pass

def layerFromName(name):
    '''
    Returns the layer from the current project with the passed name
    Returns None if no layer with that name is found
    If several layers with that name exist, only the first one is returned
    '''
    layers =_layerreg.mapLayers().values()
    for layer in layers:
        if layer.name() == name:
            return layer
    raise WrongLayerNameException()

<<<<<<< HEAD:qgiscommons/layers.py
def loadLayer(filename, name = None):
=======
def loadLayer(filename, name = None, provider=None):
>>>>>>> new_approach:qgiscommons2/layers.py
    '''
    Tries to load a layer from the given file

    :param filename: the path to the file to load.

    :param name: the name to use for adding the layer to the current project.
    If not passed or None, it will use the filename basename
    '''
    name = name or os.path.splitext(os.path.basename(filename))[0]
    qgslayer = QgsVectorLayer(filename, name, provider)
    if not qgslayer.isValid():
        qgslayer = QgsRasterLayer(filename, name, provider)
        if not qgslayer.isValid():
            raise RuntimeError('Could not load layer: ' + unicode(filename))

    return qgslayer

<<<<<<< HEAD:qgiscommons/layers.py
def loadLayerNoCrsDialog(filename, name=None):
=======

def loadLayerNoCrsDialog(filename, name=None, provider=None):
>>>>>>> new_approach:qgiscommons2/layers.py
    '''
    Tries to load a layer from the given file
    Same as the loadLayer method, but it does not ask for CRS, regardless of current 
    configuration in QGIS settings
    '''
    settings = QTCore.QSettings()
    prjSetting = settings.value('/Projections/defaultBehaviour')
    settings.setValue('/Projections/defaultBehaviour', '')
    layer = loadLayer(filename, name, provider)
    settings.setValue('/Projections/defaultBehaviour', prjSetting)
    return layer

<<<<<<< HEAD:qgiscommons/layers.py
def loadVector(path, name=None, provider="ogr"):
    """
    Loads a vector layer and returns the QgsVectorLayer instance.
    :param path: Path to the vector layer.
    :param name: The name of the new layer.
    :param provider: The provider to open this layer with defaults to ogr.
    :return: A QgsVectorLayer instance for the layer.
    """
    if not name:
        name = os.path.basename(path)
    layer = QgsVectorLayer(path, name, provider)
    return layer

=======
>>>>>>> new_approach:qgiscommons2/layers.py

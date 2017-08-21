from utils import _callerName
import shutil
import os
from PyQt4.QtCore import QDir
from PyQt4.QtGui import QFileDialog
import uuid
import time

<<<<<<< HEAD:qgiscommons/files.py
=======
from qgis.PyQt.QtCore import QDir
from qgis.PyQt.QtGui import QFileDialog

from qgiscommons2.utils import _callerName


>>>>>>> new_approach:qgiscommons2/files.py
def removeTempFolder(namespace = None):
    namespace = namespace or _callerName().split(".")[0]
    shutil.rmtree(tempFolder(namespace))
    
def tempFolder(namespace = None):
    namespace = namespace or _callerName().split(".")[0]
    tempDir = os.path.join(unicode(QDir.tempPath()), namespace)
    if not QDir(tempDir).exists():
        QDir().mkpath(tempDir)
    return unicode(os.path.abspath(tempDir))

<<<<<<< HEAD:qgiscommons/files.py
=======
def tempFilename(ext = None, namespace = None):
    ext = "." + ext if ext is not None else ""
    filename = os.path.join(tempFolder(), str(time.time()) + ext)
    return filename

>>>>>>> new_approach:qgiscommons2/files.py
def tempFilenameInTempFolder(basename, namespace = None):
    path = tempFolder(namespace)
    folder = os.path.join(path, str(uuid.uuid4()).replace("-",""))
    if not QDir(folder).exists():
        QDir().mkpath(folder)
    filename =  os.path.join(folder, basename)
    return filename

def tempFolderInTempFolder(namespace = None):
    path = tempFolder(namespace)
    folder = os.path.join(path, str(uuid.uuid4()).replace("-",""))
    if not QDir(folder).exists():
        QDir().mkpath(folder)
    return folder

from utils import _callerName
import shutil
import os
from PyQt4.QtCore import QDir
from PyQt4.QtGui import QFileDialog
import uuid

_tempFolders = {}
def removeTempFolder(namespace = None):
    namespace = namespace or _callerName().split(".")[0]
    shutil.rmtree(tempFolder(namespace))
    
def tempFolder(namespace = None):
    namespace = namespace or _callerName().split(".")[0]
    tempDir = os.path.join(unicode(QDir.tempPath()), namespace)
    if not QDir(tempDir).exists():
        QDir().mkpath(tempDir)
    return unicode(os.path.abspath(tempDir))

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

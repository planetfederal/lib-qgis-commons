from utils import _callerName
import shutil
import os
from PyQt4.QtCore import QDir
from PyQt4.QtGui import QFileDialog
import uuid

def removeTempFolder():
    shutil.rmtree(tempFolder())
    
def tempFolder():
    tempDir = os.path.join(unicode(QDir.tempPath()), _callerName())
    if not QDir(tempDir).exists():
        QDir().mkpath(tempDir)
    return unicode(os.path.abspath(tempDir))

def tempFilenameInTempFolder(basename):
    path = tempFolder()
    folder = os.path.join(path, str(uuid.uuid4()).replace("-",""))
    if not QDir(folder).exists():
        QDir().mkpath(folder)
    filename =  os.path.join(folder, basename)
    return filename

def tempFolderInTempFolder():
    path = tempFolder()
    folder = os.path.join(path, str(uuid.uuid4()).replace("-",""))
    if not QDir(folder).exists():
        QDir().mkpath(folder)
    return folder

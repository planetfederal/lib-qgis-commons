from utils import *
from PyQt4 import QtGui, QtCore
from qgis.core import *
import inspect
import os

from PyQt4 import uic

def load_ui(name):
    if os.path.exists(name):
        uifile = name
    else:
        frame = inspect.stack()[1]
        filename = inspect.getfile(frame[0])
        uifile = os.path.join(os.path.dirname(filename), name)
        if not os.path.exists(uifile):
            uifile = os.path.join(os.path.dirname(filename), "ui", name)

    widget, base = uic.loadUiType(uifile)
    return widget, base

LAST_PATH = "LAST_PATH"

def ask_for_files(parent, msg = None, isSave = False, allowMultiple = False, exts = "*"):
    '''
    Asks for a file or files, opening the corresponding dialog with the last path that was selected 
    when this same function was invoked from the calling method. 

    :param parent: The parent window
    :param msg: The message to use for the dialog title
    :param isSave: true if we are asking for file to save
    :param allowMultiple: True if should allow multiple files to be selected. Ignored if isSave == True
    :param exts: Extensions to allow in the file dialog. Can be a single string or a list of them. 
    Use "*" to add an option that allows all files to be selected 

    :returns: A string with the selected filepath or an array of them, depending on whether allowMultiple is True of False
    '''
    msg = msg or 'Select file'
    name = _callerName()
    path = plugin_setting(LAST_PATH, name)
    f = None
    if not isinstance(exts, list):
        exts = [exts]
    extString = ";; ".join([" %s files (*.%s)" % (e.upper(), e) if e != "*" else "All files (*.*)" for e in exts])
    if allowMultiple:
        ret = QtGui.QFileDialog.getOpenFileNames(parent, msg, path, '*.' + extString)
        if ret:
            f = ret[0]
        else:
            f = ret = None
    else:
        if isSave:
            ret = QtGui.QFileDialog.getSaveFileName(parent, msg, path, '*.' + extString) or None
            if ret is not None and not ret.endswith(exts[0]):
                ret += "." + exts[0]
        else:
            ret = QtGui.QFileDialog.getOpenFileName(parent, msg , path, '*.' + extString) or None
        f = ret

    if f is not None:
        set_plugin_setting(LAST_PATH, name, os.path.dirname(f))

    return ret

def ask_for_folder(parent, msg = None):
        '''
    Asks for a folder, opening the corresponding dialog with the last path that was selected 
    when this same function was invoked from the calling method

    :param parent: The parent window
    :param msg: The message to use for the dialog title
    '''
    msg = msg or 'Select folder'
    name = _callerName()
    path = plugin_setting(LAST_PATH, name)
    folder =  QtGui.QFileDialog.getExistingDirectory(parent, "Select folder to store app", path)
    if folder:
        set_plugin_setting(LAST_PATH, name, folder)
    return folder



#=============

_dialog = None

class ExecutorThread(QtCore.QThread):

    finished = QtCore.pyqtSignal()

    def __init__(self, func):
        QtCore.QThread.__init__(self, iface.mainWindow())
        self.func = func
        self.returnValue = None
        self.exception = None

    def run (self):
        try:
            self.returnValue = self.func()
        except Exception, e:
            self.exception = e
        finally:
            self.finished.emit()

def execute(func, message = None):
    '''
    Executes a lengthy tasks in a separate thread and displays a waiting dialog if needed.
    Sets the cursor to wait cursor while the task is running.

    This function does not provide any support for progress indication

    :param func: The function to execute.

    :param message: The message to display in the wait dialog. If not passed, the dialog won't be shown
    '''
    global _dialog
    cursor = QtGui.QApplication.overrideCursor()
    waitCursor = (cursor is not None and cursor.shape() == QtCore.Qt.WaitCursor)
    dialogCreated = False
    try:
        QtCore.QCoreApplication.processEvents()
        if not waitCursor:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        if message is not None:
            t = ExecutorThread(func)
            loop = QtCore.QEventLoop()
            t.finished.connect(loop.exit, QtCore.Qt.QueuedConnection)
            if _dialog is None:
                dialogCreated = True
                _dialog = QtGui.QProgressDialog(message, "Running", 0, 0, iface.mainWindow())
                _dialog.setWindowTitle("Running")
                _dialog.setWindowModality(QtCore.Qt.WindowModal);
                _dialog.setMinimumDuration(1000)
                _dialog.setMaximum(100)
                _dialog.setValue(0)
                _dialog.setMaximum(0)
                _dialog.setCancelButton(None)
            else:
                oldText = _dialog.labelText()
                _dialog.setLabelText(message)
            QtGui.QApplication.processEvents()
            t.start()
            loop.exec_(flags = QtCore.QEventLoop.ExcludeUserInputEvents)
            if t.exception is not None:
                raise t.exception
            return t.returnValue
        else:
            return func()
    finally:
        if message is not None:
            if dialogCreated:
                _dialog.reset()
                _dialog = None
            else:
                _dialog.setLabelText(oldText)
        if not waitCursor:
            QtGui.QApplication.restoreOverrideCursor()
        QtCore.QCoreApplication.processEvents()            
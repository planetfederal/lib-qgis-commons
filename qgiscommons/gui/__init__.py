from qgiscommons.utils import _callerName, _callerPath
from qgiscommons.settings import *
from PyQt4 import QtGui, QtCore
from qgis.core import *
import inspect
import os

from PyQt4 import uic

from pyplugin_installer.installer_data import plugins

_aboutActions = {}
def addAboutMenu(menuName, parentMenuFunction=None):
    '''
    Adds an 'about...' menu to the plugin menu.
    This method should be called from the initGui() method of the plugin

    :param menuName: The name of the plugin menu in which the about menu is to be added
    '''

    parentMenuFunction = parentMenuFunction or iface.addPluginToMenu
    namespace = _callerPath().split(".")[0]
    path = os.path.join(os.path.dirname(_callerPath()), "metadata.txt")
    aboutAction = QAction(
        QgsApplication.getThemeIcon('/mActionHelpContents.svg'),
        "About...",
        iface.mainWindow())
    aboutAction.setObjectName(namespace + "about")
    aboutAction.triggered.connect(lambda: openAboutDialog(namespace))
    parentMenuFunction(menuName, aboutAction)
    global _aboutActions
    _aboutActions[menuName] = aboutAction

def removeAboutMenu(menuName, parentMenuFunction=None):
    global _aboutActions
    parentMenuFunction = parentMenuFunction or iface.removePluginMenu
    parentMenuFunction(menuName, _aboutActions[menuName])
    action = _aboutActions.pop(menuName, None)
    action.deleteLater()


def openAboutDialog(namespace):
    plugin = plugins.all()[namespace]

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("%s\n\n%s" % (plugin["name"], plugin["description"]))
    msg.setWindowTitle("Plugin info")
    msg.setDetailedText(_pluginDetails(namespace))
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg.exec_()

def _pluginDetails(namespace):
    plugin = plugins.all()[namespace]
    html = '<style>body, table {padding:0px; margin:0px; font-family:verdana; font-size: 1.1em;}</style>'
    html += '<body>'
    html += '<table cellspacing="4" width="100%"><tr><td>'
    html += '<h1>{}</h1>'.format(plugin['name'])
    html += '<h3>{}</h3>'.format(plugin['description'])

    if plugin['about'] != '':
        html += plugin['about'].replace('\n', '<br/>')

    html += '<br/><br/>'

    if plugin['category'] != '':
        html += '{}: {} <br/>'.format(tr('Category'), plugin['category'])

    if plugin['tags'] != '':
        html += '{}: {} <br/>'.format(tr('Tags'), plugin['tags'])

    if plugin['homepage'] != '' or plugin['tracker'] != '' or plugin['code_repository'] != '':
        html += tr('More info:')

        if plugin['homepage'] != '':
            html += '<a href="{}">{}</a> &nbsp;'.format(plugin['homepage'], tr('homepage') )

        if plugin['tracker'] != '':
            html += '<a href="{}">{}</a> &nbsp;'.format(plugin['tracker'], tr('bug_tracker') )

        if plugin['code_repository'] != '':
            html += '<a href="{}">{}</a> &nbsp;'.format(plugin['code_repository'], tr('code_repository') )

        html += '<br/>'

    html += '<br/>'

    if plugin['author_email'] != '':
        html += '{}: <a href="mailto:{}">{}</a>'.format(tr('Author'), plugin['author_email'], plugin['author_name'])
        html += '<br/><br/>'
    elif plugin['author_name'] != '':
        html += '{}: {}'.format(tr('Author'), plugin['author_name'])
        html += '<br/><br/>'

    if plugin['version_installed'] != '':
        ver = plugin['version_installed']
        if ver == '-1':
            ver = '?'

        html += tr('Installed version: {} (in {})<br/>'.format(ver, plugin['library']))

    if plugin['version_available'] != '':
        html += tr('Available version: {} (in {})<br/>'.format(plugin['version_available'], plugin['zip_repository']))

    if plugin['changelog'] != '':
        html += '<br/>'
        changelog = tr('Changelog:<br/>{} <br/>'.format(plugin['changelog']))
        html += changelog.replace('\n', '<br/>')

    html += '</td></tr></table>'
    html += '</body>'

    return html

def tr(s):
    return s

def loadUi(name):
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

def askForFiles(parent, msg = None, isSave = False, allowMultiple = False, exts = "*"):
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
    caller = _callerName().split(".")
    name = "/".join([LAST_PATH, caller[-1]])
    namespace = caller[0]
    path = pluginSetting(name, namespace)
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
        setPluginSetting(name, os.path.dirname(f), namespace)

    return ret

def askForFolder(parent, msg = None):
    '''
    Asks for a folder, opening the corresponding dialog with the last path that was selected
    when this same function was invoked from the calling method

    :param parent: The parent window
    :param msg: The message to use for the dialog title
    '''
    msg = msg or 'Select folder'
    caller = _callerName().split(".")
    name = "/".join([LAST_PATH, caller[-1]])
    namespace = caller[0]
    path = pluginSetting(name, namespace)
    folder =  QtGui.QFileDialog.getExistingDirectory(parent, msg, path)
    if folder:
        setPluginSetting(name, folder, namespace)
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

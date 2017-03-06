from utils import _callerName, _callerPath
from PyQt4.QtCore import *
import os
import json
from collections import defaultdict
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

#Types to use in the settings.json file

BOOL = "bool"
STRING = "string"
TEXT = "text" # a multile string
NUMBER = "number"
FILE = "file"
FOLDER = "folder"
CHOICE  ="choice"
CRS = "crs"

def setPluginSetting(name, value, namespace = None):
    namespace = _callerName().split(".")[0]
    QSettings().setValue(namespace + "/" + name, value)

def pluginSetting(name, namespace = None):
    namespace = namespace or _callerName().split(".")[0]
    full_name = namespace + "/" + name
    if QSettings().contains(full_name):
        v = QSettings().value(full_name, None)
        if isinstance(v, QPyNullVariant):
            v = None
        return v
    else:        
        for setting in _settings[namespace]:
            if setting["name"] == name:
                return setting["default"]        
        return None

_settings = {}

def readSettings():
    namespace = _callerName().split(".")[0]
    path = os.path.join(os.path.dirname(_callerPath()), "settings.json")
    with open(path) as f:
        _settings[namespace] = json.load(f)

def addSettingsMenu(menuName):
    namespace = _callerName().split(".")[0]
    settingsIcon = QgsApplication.getThemeIcon('/mActionHelpAPI.png')
    settingsAction = QAction(settingsIcon, "Settings...", iface.mainWindow())
    settingsAction.setObjectName(namespace + "settings")
    settingsAction.triggered.connect(lambda: openSettingsDialog(namespace))
    iface.addPluginToMenu(menuName, settingsAction)

def openSettingsDialog(namespace):
    print namespace
    dlg = ConfigDialog(namespace)
    dlg.exec_()

#########################################

class ConfigDialog(QDialog):

    def __init__(self, namespace):
        self.settings = _settings[namespace]
        print self.settings
        self.namespace = namespace
        QDialog.__init__(self)
        self.setupUi()
        if hasattr(self.searchBox, 'setPlaceholderText'):
            self.searchBox.setPlaceholderText(self.tr("Search..."))
        self.searchBox.textChanged.connect(self.filterTree)
        self.fillTree()
        self.tree.expandAll()

    def setupUi(self):
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.resize(640, 450)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.searchBox = QgsFilterLineEdit(self)
        self.verticalLayout.addWidget(self.searchBox)
        self.tree = QTreeWidget(self)
        self.tree.setAlternatingRowColors(True)
        self.verticalLayout.addWidget(self.tree)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)

        self.setWindowTitle("Configuration options")
        self.searchBox.setToolTip("Enter setting name to filter list")
        self.tree.headerItem().setText(0, "Setting")
        self.tree.headerItem().setText(1, "Value")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


    def filterTree(self):
        text = unicode(self.searchBox.text())
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            visible = False
            for j in range(item.childCount()):
                subitem = item.child(j)
                itemText = subitem.text(0)
            if (text.strip() == ""):
                subitem.setHidden(False)
                visible = True
            else:
                hidden = text not in itemText
                item.setHidden(hidden)
                visible = visible or not hidden
            item.setHidden(not visible)
            item.setExpanded(visible and text.strip() != "")

    def fillTree(self):
        self.items = {}
        self.tree.clear()

        grouped = defaultdict(list)
        for setting in self.settings:
            grouped[setting["group"]].append(setting)
        for groupName, group in grouped.iteritems():
            item = self._getGroupItem(groupName, group)
            self.tree.addTopLevelItem(item)

        self.tree.setColumnWidth(0, 400)


    def _getGroupItem(self, groupName, params):
        print params
        item = QTreeWidgetItem()
        item.setText(0, groupName)
        icon = QIcon(os.path.join(os.path.dirname(__file__), "setting.png"))
        item.setIcon(0, icon)
        for param in params:
            value = pluginSetting(param["name"], self.namespace)
            subItem = TreeSettingItem(item, self.tree, param, self.namespace, value)
            item.addChild(subItem)
        return item


    def accept(self):
        iterator = QTreeWidgetItemIterator(self.tree)
        value = iterator.value()
        while value:
            if hasattr(value, 'saveValue'):
                value.saveValue()
            iterator += 1
            value = iterator.value()
        QDialog.accept(self)



class TreeSettingItem(QTreeWidgetItem):

    comboStyle = '''QComboBox {
                 border: 1px solid gray;
                 border-radius: 3px;
                 padding: 1px 18px 1px 3px;
                 min-width: 6em;
             }

             QComboBox::drop-down {
                 subcontrol-origin: padding;
                 subcontrol-position: top right;
                 width: 15px;
                 border-left-width: 1px;
                 border-left-color: darkgray;
                 border-left-style: solid;
                 border-top-right-radius: 3px;
                 border-bottom-right-radius: 3px;
             }
            '''

    def __init__(self, parent, tree, setting, namespace, value):
        QTreeWidgetItem.__init__(self, parent)
        self.parent = parent
        self.namespace = namespace
        self.tree = tree
        self._value = value
        self.name = setting["name"]
        self.settingType = setting["type"]
        self.setText(0, self.name)
        if self.settingType == CRS:
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            self.crsLabel = QLabel()
            self.crsLabel.setText(value)
            self.label = QLabel()
            self.label.setText("<a href='#'> Edit</a>")
            self.crsLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(self.crsLabel)
            layout.addWidget(self.label)
            self.newValue = value
            def edit():
                selector = QgsGenericProjectionSelector()
                selector.setSelectedAuthId(value)
                if selector.exec_():
                    authId = selector.selectedAuthId()
                    if authId.upper().startswith("EPSG:"):
                        self.newValue = authId
                        self.crsLabel.setText(authId)
            self.label.connect(self.label, SIGNAL("linkActivated(QString)"), edit)
            w = QWidget()
            w.setLayout(layout)
            self.tree.setItemWidget(self, 1, w)
        elif self.settingType == BOOL:
            if value:
                self.setCheckState(1, Qt.Checked)
            else:
                self.setCheckState(1, Qt.Unchecked)
        elif self.settingType == CHOICE:
            self.combo = QComboBox()
            self.combo.setStyleSheet(self.comboStyle)
            for option in setting["options"]:
                self.combo.addItem(option)
            self.tree.setItemWidget(self, 1, self.combo)
            idx = self.combo.findText(str(value))
            self.combo.setCurrentIndex(idx)
        elif self.settingType == TEXT:
            self.label = QLabel()
            self.label.setText("<a href='#'>Edit</a>")
            self.newValue = value
            def edit():
                dlg = TextEditorDialog(unicode(self.newValue), JSON)
                dlg.exec_()
                self.newValue = dlg.text
            self.label.connect(self.label, SIGNAL("linkActivated(QString)"), edit)
            self.tree.setItemWidget(self, 1, self.label)
        else:
            self.setFlags(self.flags() | Qt.ItemIsEditable)
            self.setText(1, unicode(value))


    def saveValue(self):
        value = self.value()
        setPluginSetting(self.value, self.namespace)

    def value(self):
        self.setBackgroundColor(0, Qt.white)
        self.setBackgroundColor(1, Qt.white)
        try:
            if self.settingType == BOOL:
                return self.checkState(1) == Qt.Checked
            elif self.settingType == NUMBER:
                return float(self.text(1))
            elif self.settingType == CHOICE:
                return self.combo.currentText()
            elif self.settingType in [TEXT, CRS]:
                return self.newValue
            else:
                return self.text(1)
        except:
            self.setBackgroundColor(0, Qt.yellow)
            self.setBackgroundColor(1, Qt.yellow)
            raise WrongValueException()

    def setValue(self, value):
        if self.settingType == BOOL:
            if value:
                self.setCheckState(1, Qt.Checked)
            else:
                self.setCheckState(1, Qt.Unchecked)
        elif self.settingType == CHOICE:
            idx = self.combo.findText(str(value))
            self.combo.setCurrentIndex(idx)
        elif self.settingType == TEXT:
            self.newValue = value
        elif self.settingType == CRS:
            self.newValue = value
            self.crsLabel.setText(value)
        else:
            self.setText(1, unicode(value))


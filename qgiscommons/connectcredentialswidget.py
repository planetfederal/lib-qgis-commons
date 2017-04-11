# -*- coding: utf-8 -*-

"""
***************************************************************************
    connectcredentialswidget.py
    ---------------------
    Date                 : April 2017
    Copyright            : (C) 2017 Boundless, http://boundlessgeo.com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'April 2017'
__copyright__ = '(C) 2017 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QWidget, QLabel, QDialogButtonBox, QVBoxLayout

from qgiscommons.iconlineedit import IconLineEdit
from qgiscommons.passwordlineedit import PasswordLineEdit

iconsPath = os.path.join(os.path.dirname(__file__), "icons")


class ConnectCredentialsWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.leLogin = IconLineEdit(self)
        self.leLogin.setIcon(QIcon(os.path.join(iconsPath, "envelope.svg")))
        self.leLogin.setPlaceholderText("Email")

        self.lePassword = PasswordLineEdit(self)

        self.lblResetPassword = QLabel(self)
        self.lblResetPassword.setAlignment(Qt.AlignCenter)
        self.lblResetPassword.setOpenExternalLinks(True)
        self.lblResetPassword.setTextInteractionFlags(Qt.LinksAccessibleByKeyboard | Qt.LinksAccessibleByMouse)
        self.lblResetPassword.setText("<html><head/><body><p><a href='https://boundlessgeo.auth0.com/login?client=rmtncamSKiwRBuVYTvFYJGtTspVuplMh'><span style='text-decoration: underline; color:#0000ff;'>Don't remember your password?</span></a></p></body></html>")

        self.lblRegister = QLabel(self)
        self.lblRegister.setAlignment(Qt.AlignCenter)
        self.lblRegister.setOpenExternalLinks(True)
        self.lblRegister.setTextInteractionFlags(Qt.LinksAccessibleByKeyboard | Qt.LinksAccessibleByMouse)
        self.lblRegister.setText("<html><head/><body><p><a href='https://connect.boundlessgeo.com'><span style='text-decoration: underline; color:#0000ff;'>Don't have an account?</span></a></p></body></html>")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.leLogin)
        self.layout.addWidget(self.lePassword)
        self.layout.addWidget(self.lblResetPassword)
        self.layout.addWidget(self.lblRegister)
        self.setLayout(self.layout)

    def login(self):
        return self.leLogin.text()

    def setLogin(self, login):
        self.leLogin.setText(login)

    def password(self):
        return self.lePassword.text()

    def setPassword(self, password):
        self.lePassword.setText(password)

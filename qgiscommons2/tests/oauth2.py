#!/usr/bin/env python
# Tests for Travis CI.
# This test can be run from the command line as a normal
# python script


import os
import re
import sys
import shutil
import unittest
import tempfile


__author__ = 'Alessandro Pasotti'
__date__ = 'March 2017'
__copyright__ = '(C) 2017 Boundless, http://boundlessgeo.com'


MAPS_URI = "https://api.test.boundlessgeo.io/v1/basemaps/"
PROVIDERS_URI = "https://api.dev.boundlessgeo.io/v1/basemaps/providers/"
TOKEN_URI = "https://api.test.boundlessgeo.io/v1/token/oauth/"
AUTHDB_MASTERPWD = "pass"
TEST_AUTHCFG_ID = "cone999"  # test id
TEST_AUTHCFG_NAME = "Boundless BCS API OAuth2 - TEST"
# To be used by command line tests, when inside QGIS, the AUTHDBDIR
# is not needed as the auth DB is initialized by QGIS authentication system
# initialization
AUTHDBDIR = None

from qgiscommons2.network import oauth2
from qgis.PyQt.QtCore import QFileInfo, Qt
from qgis.core import QgsProject, QgsApplication, QgsAuthManager



class OAuth2Test(unittest.TestCase):

    AUTHM = None

    def setUp(self):
        for c in self.authm.availableAuthMethodConfigs().values():
            if c.id() == TEST_AUTHCFG_ID:
                assert self.authm.removeAuthenticationConfig(c.id())
        if (not self.authm.masterPasswordIsSet()
                or not self.authm.masterPasswordHashInDb()):
            if AUTHDBDIR is not None or not self.authm.masterPasswordHashInDb():
                msg = 'Failed to store and verify master password in auth db'
                assert self.authm.setMasterPassword(self.mpass, True), msg
            else:
                msg = 'Master password is not valid'
                assert self.authm.setMasterPassword(True), msg

    @classmethod
    def setUpClass(cls):
        cls.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        cls.authcfg = None
        if hasattr(QgsApplication, 'authManager'):
            cls.authm = QgsApplication.authManager()  # QGIS 3
        else:
            cls.authm = QgsAuthManager.instance()  # QGIS 2
        assert cls.authm is not None, 'QgsAuthManager instance not available'
        assert not cls.authm.isDisabled(), cls.authm.disabledMessage()
        cls.mpass = AUTHDB_MASTERPWD  # master password

        if AUTHDBDIR is not None:
            db1 = QFileInfo(cls.authm.authenticationDbPath()).canonicalFilePath()
            db2 = QFileInfo(AUTHDBDIR + '/qgis-auth.db').canonicalFilePath()
            msg = 'Auth db temp path does not match db path of manager'
            assert db1 == db2, msg

    @classmethod
    def tearDownClass(cls):
        if AUTHDBDIR is not None:
            try:
                shutil.rmtree(AUTHDBDIR)
            except:
                pass

    @unittest.skipIf(not oauth2.oauth2_supported(), "OAuth2 not supported")
    def test_create_oauth_authcfg(self):
        """Create an authentication configuration"""
        self.assertEquals(oauth2.setup_oauth('username', 'password', TOKEN_URI, TEST_AUTHCFG_ID, TEST_AUTHCFG_NAME), TEST_AUTHCFG_ID)


    @unittest.skipIf(not oauth2.oauth2_supported(), "OAuth2 not supported")
    def test_get_oauth_authcfg(self):
        """Retrieve the OAuth2 authentication configuration"""
        self.assertEquals(oauth2.setup_oauth('username', 'password', TOKEN_URI, TEST_AUTHCFG_ID, TEST_AUTHCFG_NAME), TEST_AUTHCFG_ID)
        self.assertEquals(oauth2.get_oauth_authcfg(TEST_AUTHCFG_ID).id(), TEST_AUTHCFG_ID)


def pluginSuite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(OAuth2Test, 'test'))
    return suite


def unitTests():
    _tests = []
    _tests.extend(pluginSuite())
    return _tests

# run all tests, this function is automatically called by the travis CI
# from the qgis-testing-environment-docker system


def run_all():
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(pluginSuite())


if __name__ == '__main__':
    AUTHDBDIR = tempfile.mkdtemp()
    os.environ['QGIS_AUTH_DB_DIR_PATH'] = AUTHDBDIR
    QgsApplication.setPrefixPath('/usr/', True)
    qgs = QgsApplication([], True)
    qgs.initQgis()
    unittest.main()

#from future import standard_library
#standard_library.install_aliases()
#import unittest
import unittest
import tempfile
import time
import re
import os
import signal
import sip
import subprocess
from qgis.testing import (
    start_app
)
from utilities import waitServer
from qgiscommons.networkaccessmanager import (
    NetworkAccessManager,
    Response,
    RequestsException,
    RequestsExceptionTimeout,
    RequestsExceptionConnectionError,
    RequestsExceptionUserAbort,

)
from qgis.PyQt.QtCore import QSettings


# If True, will use http://httpbin.org
USE_ONLINE_HTTPBIN = os.environ.get('USE_ONLINE_HTTPBIN', False)

for c in ('QDate', 'QDateTime', 'QString', 'QTextStream', 'QTime', 'QUrl', 'QVariant'):
    sip.setapi(c, 2)

QGIS_AUTH_DB_DIR_PATH = tempfile.mkdtemp()

os.environ['QGIS_AUTH_DB_DIR_PATH'] = QGIS_AUTH_DB_DIR_PATH

qgis_app = start_app()

get_expected = '''{
  "args": {},
  "headers": {
    "Accept-Encoding": "gzip",
    "Accept-Language": "en-US,*",
    "Connection": "Keep-Alive",
    "Host": "127.0.0.1:8000",
    "User-Agent": "Mozilla/5.0 QGIS/2.18.5"
  },
  "origin": "127.0.0.1",
  "url": "http://127.0.0.1:8000/get"
}
'''

class TestNetworkAccessManager(unittest.TestCase):

    timeoutEntry = '/Qgis/networkAndProxy/networkTimeout'

    @classmethod
    def setUpClass(cls):
        # setup network timeout
        cls.settings = QSettings()
        cls.settings.setValue(cls.timeoutEntry, 60000)

        if USE_ONLINE_HTTPBIN:
            cls.serverUrl = 'https://httpbin.org'
            return

        # start httpbin server locally
        cls.server = subprocess.Popen(['gunicorn', 'httpbin:app'],
                                      env=os.environ, stdout=subprocess.PIPE)
        cls.port = 8000
        cls.hostname = '127.0.0.1'
        cls.protocol = 'http'
        cls.serverUrl = '{0}://{1}:{2}'.format(cls.protocol, cls.hostname, cls.port)
        # Wait for the server process to start
        assert waitServer(cls.serverUrl, timeout=2), "Server is not responding! {}".format(cls.serverUrl)

    @classmethod
    def tearDownClass(cls):
        """Run after all tests"""
        return
        cls.server.terminate()
        del cls.server

    def setUp(self):
        """Run before each test."""
        pass

    def tearDown(self):
        """Run after each test."""
        pass

    def test_initNAM(self):
        """Test nam.__init__."""
        # default and init values
        initValueFor_http_call_result = Response({
            'status': 0,
            'status_code': 0,
            'status_message': '',
            'content' : '',
            'ok': False,
            'headers': {},
            'reason': '',
            'exception': None,
        })

        nam = NetworkAccessManager()
        self.assertEqual(nam.disable_ssl_certificate_validation, False)
        self.assertEqual(nam.authid, None)
        self.assertEqual(nam.reply, None)
        self.assertEqual(nam.debug, True)
        self.assertEqual(nam.exception_class, None)
        self.assertEqual(nam.reply, None)
        self.assertEqual(nam.on_abort, False)
        self.assertEqual(nam.blocking_mode, False)
        self.assertEqual(nam.http_call_result, initValueFor_http_call_result)

        # passed values
        authid = '1234567'
        exception_class = Exception()
        nam = NetworkAccessManager(authid=authid, disable_ssl_certificate_validation=True, exception_class=exception_class, debug=False)
        self.assertEqual(nam.disable_ssl_certificate_validation, True)
        self.assertEqual(nam.authid, authid)
        self.assertEqual(nam.debug, False)
        self.assertEqual(nam.exception_class, exception_class)

    def test_syncNAM_success(self):
        """Test NAM in sync mode."""
        # test success
        nam = NetworkAccessManager(debug=True)
        (response, content) = nam.request(self.serverUrl+'/get')
        self.assertTrue(response.ok)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, get_expected)

    def test_syncNAM_url_not_found(self):
        # test Url not found
        try:
            nam = NetworkAccessManager(debug=True)
            (response, content) = nam.request(self.serverUrl+'/somethingwrong')
        except RequestsException as ex:
            self.assertTrue('server replied: NOT FOUND' in str(ex))
        except Exception as ex:
            raise ex

    def test_syncNAM_local_timeout(self):
        # test url timeout by client timout
        self.timeoutOriginal = self.settings.value(self.timeoutEntry)
        self.settings.setValue(self.timeoutEntry, 1000)
        nam = NetworkAccessManager(debug=True)
        with self.assertRaises(RequestsExceptionTimeout):
            (response, content) = nam.request(self.serverUrl+'/delay/60')
        self.settings.setValue(self.timeoutEntry, self.timeoutOriginal)


    def test_syncNAM_unathorised(self):
        # connection refused http 401
        try:
            nam = NetworkAccessManager(debug=True)
            (response, content) = nam.request(self.serverUrl+'/status/401')
        except RequestsException as ex:
            self.assertTrue('Host requires authentication' in str(ex))
        except Exception as ex:
            raise ex

    def test_syncNAM_forbidden(self):
        # connection refused http 403
        try:
            nam = NetworkAccessManager(debug=True)
            (response, content) = nam.request(self.serverUrl+'/status/401')
        except RequestsException as ex:
            self.assertTrue('Host requires authentication' in str(ex))
        except Exception as ex:
            raise ex

    def test_syncNAM_redirect(self):
        # connection redirection
        try:
            nam = NetworkAccessManager(debug=True)
            (response, content) = nam.request(self.serverUrl+'/redirect-to?url=pippo')
        except RequestsException as ex:
            self.assertTrue('Host requires authentication' in str(ex))
        except Exception as ex:
            raise ex


###############################################################################

def suiteSubset():
    tests = ['testOpenWFSLayer']
    suite = unittest.TestSuite(map(PKIOWSTests, tests))
    return suite


def suite():
    suite = unittest.makeSuite(PKIOWSTests, 'test')
    return suite


# run all tests using unittest skipping nose or testplugin
def run_all():
    # demo_test = unittest.TestLoader().loadTestsFromTestCase(PKIOWSTests)
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())


# run a subset of tests using unittest skipping nose or testplugin
def run_subset():
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suiteSubset())


if __name__ == '__main__':
    unittest.main()

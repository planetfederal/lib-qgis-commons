#from future import standard_library
#standard_library.install_aliases()
#import unittest
import tempfile
import time
import re
import os
import signal
import sip
import subprocess
from qgis.testing import (
    start_app,
    unittest,
)
from utilities import waitServer
from qgiscommons.networkaccessmanager import NetworkAccessManager, Response, RequestsException

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

    @classmethod
    def setUpClass(cls):
        cls.server = subprocess.Popen(['gunicorn', 'httpbin:app'],
                                      env=os.environ, stdout=subprocess.PIPE)
        # wait for server start
        #time.sleep(1)

        cls.port = 8000
        cls.hostname = '127.0.0.1'
        cls.protocol = 'http'
        # Wait for the server process to start
        cls.serverUrl = '{0}://{1}:{2}'.format(cls.protocol, cls.hostname, cls.port)
        assert waitServer(cls.serverUrl, timeout=2), "Server is not responding! {}".format(cls.serverUrl)

    @classmethod
    def tearDownClass(cls):
        """Run after all tests"""
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
        self.assertEqual(nam.onAbort, False)
        self.assertEqual(nam.blockingMode, False)
        self.assertEqual(nam.http_call_result, initValueFor_http_call_result)

        # passed values
        authid = '1234567'
        exception_class = Exception()
        nam = NetworkAccessManager(authid=authid, disable_ssl_certificate_validation=True, exception_class=exception_class, debug=False)
        self.assertEqual(nam.disable_ssl_certificate_validation, True)
        self.assertEqual(nam.authid, authid)
        self.assertEqual(nam.debug, False)
        self.assertEqual(nam.exception_class, exception_class)

    def test_syncNAM(self):
        """Test NAM in sync mode."""
        nam = NetworkAccessManager(debug=True)
        (response, content) = nam.request(self.serverUrl+'/get')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content, get_expected)

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

#from future import standard_library
#standard_library.install_aliases()
#import unittest
import unittest
import tempfile
import time
import re
import os
import sys
import signal
import sip
import subprocess
from qgis.core import QgsNetworkAccessManager
from qgis.PyQt import QtCore
from qgis.testing import (
    start_app
)
from utilities import waitServer
from qgiscommons2.network.networkaccessmanager import (
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

try:
    qgis_app = start_app()
except:
    # fail in case test is run inside a real qgis
    pass

# get_expected not used
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
    server = None

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
        if cls.server:
            cls.server.terminate()
            del cls.server
            cls.server = None

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
        self.assertEqual(nam.httpResult(), initValueFor_http_call_result)

        # passed values
        authid = '1234567'
        exception_class = Exception()
        nam = NetworkAccessManager(authid=authid, disable_ssl_certificate_validation=True, exception_class=exception_class, debug=False)
        self.assertEqual(nam.disable_ssl_certificate_validation, True)
        self.assertEqual(nam.authid, authid)
        self.assertEqual(nam.debug, False)
        self.assertEqual(nam.exception_class, exception_class)

    def test_syncNAM_customException(self):
        """Test NAM raise custom exception."""
        # test success
        class customEx(Exception):
            pass

        with self.assertRaises(customEx):
            nam = NetworkAccessManager(debug=True, exception_class=customEx)
            (response, content) = nam.request(self.serverUrl+'/somethingwrong')

    def test_syncNAM_success(self):
        """Test NAM in sync mode."""
        # test success
        nam = NetworkAccessManager(debug=True)
        (response, content) = nam.request(self.serverUrl+'/get')
        self.assertTrue(response.ok)
        self.assertEqual(response.status_code, 200)
        #self.assertEqual(content, get_expected)

    def test_syncNAM_tiff_success(self):
        """Test NAM in sync mode with binary files to check for bytearray conversion."""
        # test success
        nam = NetworkAccessManager(debug=True)
        tiff_file =os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', '1.1.01.tiff')
        # Online
        #(response, content) = nam.request("http://sipi.usc.edu/database/download.php?vol=textures&img=1.1.01")
        # Offline (I tested and they give the same result)
        (response, content) = nam.request("file://%s" % tiff_file)
        self.assertTrue(response.ok)
        # Offline has no status code
        #self.assertEqual(response.status_code, 200)
        self.assertEqual(content, open(tiff_file, 'rb').read(), "Image differs")


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
            (response, content) = nam.request(self.serverUrl+'/status/403')
        except RequestsException as ex:
            self.assertTrue('server replied: FORBIDDEN' in str(ex))
        except Exception as ex:
            raise ex

    def test_syncNAM_redirect(self):
        # connection redirection
        try:
            nam = NetworkAccessManager(debug=True)
            (response, content) = nam.request(self.serverUrl+'/redirect-to?url=./status/401')
        except RequestsException as ex:
            self.assertTrue('Host requires authentication' in str(ex))
        except Exception as ex:
            raise ex

    #######################################################
    #
    # ASYNC version
    #
    #######################################################

    def test_AsyncNAM_emptyreturn(self):
        """Test ANAM return value."""
        loop = QtCore.QEventLoop()
        nam = NetworkAccessManager(debug=True)
        ret = nam.request('anyurl', blocking=False)
        self.assertEqual(ret, (None, None))

    def test_AsyncNAM_success(self):
        """Test ANAM if it can manages success."""
        # test success
        self.checkEx = None
        def finishedListener():
            try:
                httpResult = nam.httpResult()
                self.assertTrue(httpResult.ok)
                self.assertEqual(httpResult.status_code, 200)
            except Exception as ex:
                self.checkEx = ex

        loop = QtCore.QEventLoop()
        nam = NetworkAccessManager(debug=True)
        nam.request(self.serverUrl+'/get', blocking=False)
        nam.reply.finished.connect(finishedListener)
        nam.reply.finished.connect(loop.exit, QtCore.Qt.QueuedConnection)
        loop.exec_(flags=QtCore.QEventLoop.ExcludeUserInputEvents)
        if self.checkEx:
            raise self.checkEx

    def test_AsyncNAM_tiff_success(self):
        """Test NAM in async mode with binary files to check for bytearray conversion."""
        # test success
        self.checkEx = None
        def finishedListener():
            try:
                httpResult = nam.httpResult()
                self.assertTrue(httpResult.ok)
                # No status code in offline
                #self.assertEqual(httpResult.status_code, 200)
                self.assertEqual(httpResult.content, open(tiff_file, 'rb').read(), "Image differs")
            except Exception as ex:
                self.checkEx = ex

        loop = QtCore.QEventLoop()
        tiff_file =os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', '1.1.01.tiff')
        nam = NetworkAccessManager(debug=True)
        (response, content) = nam.request("file://%s" % tiff_file, blocking=False)
        nam.reply.finished.connect(finishedListener)
        nam.reply.finished.connect(loop.exit, QtCore.Qt.QueuedConnection)
        loop.exec_(flags=QtCore.QEventLoop.ExcludeUserInputEvents)
        if self.checkEx:
            raise self.checkEx


    def test_AsyncNAM_url_not_found(self):
        """Test ANAM if it can manages 404"""
        # test Url not found
        self.checkEx = None
        def finishedListener():
            try:
                httpResult = nam.httpResult()
                self.assertEqual(httpResult.status_code, 404)
                self.assertIn('server replied: NOT FOUND', str(httpResult.exception))
            except Exception as ex:
                self.checkEx = ex

        loop = QtCore.QEventLoop()
        nam = NetworkAccessManager(debug=True)
        nam.request(self.serverUrl+'/somethingwrong', blocking=False)
        nam.reply.finished.connect(finishedListener)
        nam.reply.finished.connect(loop.exit, QtCore.Qt.QueuedConnection)
        loop.exec_(flags=QtCore.QEventLoop.ExcludeUserInputEvents)
        if self.checkEx:
            raise self.checkEx

    def test_AsyncNAM_local_timeout(self):
        """Test ANAM if it can manages operation canceled by client."""
        """!!!Note!!! that finishedListener is emitted before than timeoutListener.
        When timeoutListener is called the httpResult has been changed to notify 
        timout."""
        # test url timeout by client timout
        self.checkEx = None
        def finishedListener():
            try:
                httpResult = nam.httpResult()
                self.assertIn('Operation canceled', str(httpResult.exception))
                self.assertIsInstance(httpResult.exception, RequestsException)
            except Exception as ex:
                self.checkEx = ex

        def timeoutListener():
            try:
                httpResult = nam.httpResult()
                self.assertIn('Timeout error', str(httpResult.exception))
                self.assertIsInstance(httpResult.exception, RequestsExceptionTimeout)
            except Exception as ex:
                self.checkEx = ex

        self.timeoutOriginal = self.settings.value(self.timeoutEntry)
        self.settings.setValue(self.timeoutEntry, 1000)
        loop = QtCore.QEventLoop()
        nam = NetworkAccessManager(debug=True)
        nam.request(self.serverUrl+'/delay/60', blocking=False)
        QgsNetworkAccessManager.instance().requestTimedOut.connect(timeoutListener)
        nam.reply.finished.connect(finishedListener)
        nam.reply.finished.connect(loop.exit , QtCore.Qt.QueuedConnection)
        loop.exec_(flags = QtCore.QEventLoop.ExcludeUserInputEvents)
        self.settings.setValue(self.timeoutEntry, self.timeoutOriginal)
        if self.checkEx:
            raise self.checkEx

    def test_AsyncNAM_unathorised(self):
        """Test ANAM if it can manages 401 (Host requires authentication)"""
        # connection refused http 401
        self.checkEx = None
        def finishedListener():
            try:
                httpResult = nam.httpResult()
                self.assertIn('Host requires authentication', str(httpResult.exception))
                self.assertIsInstance(httpResult.exception, RequestsException)
            except Exception as ex:
                self.checkEx = ex

        loop = QtCore.QEventLoop()
        nam = NetworkAccessManager(debug=True)
        nam.request(self.serverUrl+'/status/401', blocking=False)
        nam.reply.finished.connect(finishedListener)
        nam.reply.finished.connect(loop.exit , QtCore.Qt.QueuedConnection)
        loop.exec_(flags = QtCore.QEventLoop.ExcludeUserInputEvents)
        if self.checkEx:
            raise self.checkEx

    def test_AsyncNAM_forbidden(self):
        """Test ANAM if it can manages 403 (forbidden)"""
        # connection refused http 403
        self.checkEx = None
        def finishedListener():
            try:
                httpResult = nam.httpResult()
                self.assertIn('server replied: FORBIDDEN', str(httpResult.exception))
                self.assertIsInstance(httpResult.exception, RequestsException)
            except Exception as ex:
                self.checkEx = ex

        loop = QtCore.QEventLoop()
        nam = NetworkAccessManager(debug=True)
        nam.request(self.serverUrl+'/status/403', blocking=False)
        nam.reply.finished.connect(finishedListener)
        nam.reply.finished.connect(loop.exit , QtCore.Qt.QueuedConnection)
        loop.exec_(flags = QtCore.QEventLoop.ExcludeUserInputEvents)
        if self.checkEx:
            raise self.checkEx

    def test_AsyncNAM_redirect(self):
        """Test ANAM if it can manages url redirect"""
        # connection redirection
        self.checkEx = None
        def finishedListener():
            try:
                httpResult = nam.httpResult()
                self.assertIn('Host requires authentication', str(httpResult.exception))
                self.assertIsInstance(httpResult.exception, RequestsException)
            except Exception as ex:
                self.checkEx = ex

        loop = QtCore.QEventLoop()
        nam = NetworkAccessManager(debug=True)
        nam.request(self.serverUrl+'/redirect-to?url=./status/401', blocking=False)
        nam.reply.finished.connect(finishedListener)
        nam.reply.finished.connect(loop.exit , QtCore.Qt.QueuedConnection)
        loop.exec_(flags = QtCore.QEventLoop.ExcludeUserInputEvents)
        if self.checkEx:
            raise self.checkEx

    def test_AsyncNAM_abort(self):
        """Test ANAM if it can manages abort during connection"""
        from threading import Timer

        # connection redirection
        self.checkEx = None
        def finishedListener():
            try:
                httpResult = nam.httpResult()
                self.assertIn('Operation canceled', str(httpResult.exception))
                self.assertIsInstance(httpResult.exception, RequestsExceptionUserAbort)
            except Exception as ex:
                self.checkEx = ex

        loop = QtCore.QEventLoop()
        nam = NetworkAccessManager(debug=True)
        nam.request(self.serverUrl+'/delay/5', blocking=False)
        nam.reply.finished.connect(finishedListener)
        nam.reply.finished.connect(loop.exit , QtCore.Qt.QueuedConnection)
        # abort after 1sec
        t = Timer(1, nam.abort)
        t.start()
        loop.exec_(flags = QtCore.QEventLoop.ExcludeUserInputEvents)
        if self.checkEx:
            raise self.checkEx

    def test_AsyncNAM_customException(self):
        """Test ANAM raise curstom exception."""
        # test success
        class customEx(Exception):
            pass

        self.checkEx = None
        def finishedListener():
            try:
                httpResult = nam.httpResult()
                self.assertIsInstance(httpResult.exception, customEx)
            except Exception as ex:
                self.checkEx = ex

        loop = QtCore.QEventLoop()
        nam = NetworkAccessManager(debug=True, exception_class=customEx)
        nam.request(self.serverUrl+'/somethingwrong', blocking=False)
        nam.reply.finished.connect(finishedListener)
        nam.reply.finished.connect(loop.exit , QtCore.Qt.QueuedConnection)
        loop.exec_(flags = QtCore.QEventLoop.ExcludeUserInputEvents)
        if self.checkEx:
            raise self.checkEx

###############################################################################

def suiteSubset():
    tests = ['test_initNAM']
    suite = unittest.TestSuite(map(TestNetworkAccessManager, tests))
    return suite


def suite():
    suite = unittest.makeSuite(TestNetworkAccessManager, 'test')
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
    #run_subset()

import unittest
import os
import sys
import sip
for c in ('QDate', 'QDateTime', 'QString', 'QTextStream', 'QTime', 'QUrl', 'QVariant'):
    sip.setapi(c, 2)

from qgiscommons2.settings import setPluginSetting, pluginSetting, readSettings

class TestSettings(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        readSettings(os.path.join(os.path.dirname(__file__), 'data', 'settings.json'))

    def test_false_bool(self):
        self.assertEqual(pluginSetting('myfalseboolsetting'), False)
        setPluginSetting('myfalseboolsetting', True)
        self.assertEqual(pluginSetting('myfalseboolsetting'), True)
        setPluginSetting('myfalseboolsetting', False)
        self.assertEqual(pluginSetting('myfalseboolsetting'), False)

    def test_true_bool(self):
        self.assertEqual(pluginSetting('mytrueboolsetting'), True)
        setPluginSetting('mytrueboolsetting', False)
        self.assertEqual(pluginSetting('mytrueboolsetting'), False)
        setPluginSetting('mytrueboolsetting', True)
        self.assertEqual(pluginSetting('mytrueboolsetting'), True)

    def testNonExistentSetting(self):
        value = pluginSetting('wrongsetting')
        self.assertIsNone(value)

    def testNoneValue(self):
        value = pluginSetting('nonenumber')
        self.assertIsNone(value)
        value = pluginSetting('nonestring')
        self.assertIsNone(value)

    



def suite():
    suite = unittest.makeSuite(TestSettings, 'test')
    return suite


def run_all():
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())



if __name__ == '__main__':
    unittest.main()

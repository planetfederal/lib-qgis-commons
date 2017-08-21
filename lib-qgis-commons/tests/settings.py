import unittest
import os
import sys
'''
import sip
for c in ('QDate', 'QDateTime', 'QString', 'QTextStream', 'QTime', 'QUrl', 'QVariant'):
    sip.setapi(c, 2)
'''
from qgiscommons.settings import setPluginSetting, pluginSetting, readSettings

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

    def test_onchange(self):
        self.assertEqual(pluginSetting('asettingwithonchange'), True)
        setPluginSetting('asettingwithonchange', False)
        self.assertEqual(pluginSetting('asettingwithonchange'), True)


    def test_onchange_modify_value(self):
        self.assertEqual(pluginSetting('asettingwithonchange2'), 2)
        setPluginSetting('asettingwithonchange2', 3)
        self.assertEqual(pluginSetting('asettingwithonchange2'), 4)

def suite():
    suite = unittest.makeSuite(TestSettings, 'test')
    return suite


def run_all():
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())



if __name__ == '__main__':
    unittest.main()

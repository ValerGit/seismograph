# -*- coding: utf-8 -*-

import unittest
from importlib import import_module

from mock import patch

from seismograph import config
from seismograph.exceptions import ConfigError
from seismograph.utils import pyv
from lib.factories import config_factory


class TestConfigCreateOptionParser(unittest.TestCase):
    def test_not_none(self):
        parser = config.create_option_parser()
        self.assertIsNotNone(parser)


class TestConfigPrepareConfig(unittest.TestCase):
    LOGGING_KEY = 'LOGGING_SETTINGS'
    GEVENT_KEY = 'GEVENT'
    THREADING_KEY = 'THREADING'
    ASYNC_SUITES_KEY = 'ASYNC_SUITES'
    ASYNC_TESTS_KEY = 'ASYNC_TESTS'
    MULTIPROCESSING_KEY = 'MULTIPROCESSING'
    STEPS_LOG_KEY = 'STEPS_LOG'
    FLOWS_LOG_KEY = 'FLOWS_LOG'
    VERBOSE_KEY = 'VERBOSE'

    def setUp(self):
        self.conf_logging_dict = {
            self.LOGGING_KEY: {
                'mock': True,
            }
        }

        self.conf_logging_list = {
            self.LOGGING_KEY: [1, 2, 3]
        }

    @patch('logging.config.dictConfig')
    def test_logging_settings_dict(self, mock_dictConfig):
        conf = config_factory.create(**self.conf_logging_dict)
        config.prepare_config(conf)
        mock_dictConfig.assert_called_with(self.conf_logging_dict.get(self.LOGGING_KEY))

    @patch('logging.config.dictConfig')
    def test_logging_settings_list(self, mock_dictConfig):
        conf = config_factory.create(**self.conf_logging_list)
        config.prepare_config(conf)
        mock_dictConfig.assert_not_called()

    def _is_multiprocessing(self, conf):
        return conf.get(self.MULTIPROCESSING_KEY) or (
            not conf.get(self.GEVENT_KEY) and
            not conf.get(self.THREADING_KEY) and
            (conf.get(self.ASYNC_SUITES_KEY) or conf.get(self.ASYNC_TESTS_KEY))
        )

    def _is_verbose(self, conf):
        return conf.get(self.VERBOSE_KEY) or (
                                                 conf.get(self.STEPS_LOG_KEY) or
                                                 conf.get(self.FLOWS_LOG_KEY)
                                             ) and not conf.get(self.VERBOSE_KEY)

    def _gen_bool_vars(self):
        VARS = [
            self.MULTIPROCESSING_KEY,
            self.GEVENT_KEY,
            self.THREADING_KEY,
            self.ASYNC_SUITES_KEY,
            self.ASYNC_TESTS_KEY,
            self.STEPS_LOG_KEY,
            self.FLOWS_LOG_KEY,
            self.VERBOSE_KEY
        ]
        NUM_OF_VARS = len(VARS)

        for i in range(0, 2 ** NUM_OF_VARS):
            bools = map(lambda x: x == '1', list(('{0:0' + str(NUM_OF_VARS) + 'b}').format(i)))
            res = dict(zip(
                VARS,
                bools
            ))
            yield res

    def test_multithreading(self):
        for conf_data in self._gen_bool_vars():
            conf = config_factory.create(**conf_data)
            config.prepare_config(conf)

            expected = self._is_multiprocessing(conf)
            real = conf.get(self.MULTIPROCESSING_KEY)

            self.assertEquals(real, expected,
                              str(conf_data) + " {} real: {} expected: {}".format(self.MULTIPROCESSING_KEY, real,
                                                                                  expected))

    def test_verbose(self):
        for conf_data in self._gen_bool_vars():
            conf = config_factory.create(**conf_data)
            config.prepare_config(conf)

            expected = self._is_verbose(conf)
            real = conf.get(self.VERBOSE_KEY)

            self.assertEquals(real, expected,
                              str(conf_data) + " {} real: {} expected: {}".format(self.VERBOSE_KEY, real,
                                                                                  expected))


class TestConfigGetConfigPathByEnv(unittest.TestCase):
    KEY = "ENV_VAR_KEY"
    BASE_PATH = "BASE_PATH"
    DEFAULT = "DEFAULT"
    VAL = "VAL"

    @patch('os.getenv')
    def test_none_no_default(self, mock_getenv):
        mock_getenv.return_value = None
        self.assertEquals(config.get_config_path_by_env(self.KEY), None)
        self.assertEquals(config.get_config_path_by_env(self.KEY, base_path=self.BASE_PATH), None)

    @patch('os.getenv')
    def test_val_no_default(self, mock_getenv):
        mock_getenv.return_value = self.VAL
        self.assertEquals(config.get_config_path_by_env(self.KEY), self.VAL)
        self.assertEquals(config.get_config_path_by_env(self.KEY, base_path=self.BASE_PATH), self.BASE_PATH + self.VAL)

    @patch('os.getenv')
    def test_none_with_default(self, mock_getenv):
        mock_getenv.return_value = self.DEFAULT
        self.assertEquals(config.get_config_path_by_env(self.KEY, default=self.DEFAULT), self.DEFAULT)
        mock_getenv.assert_called_with(self.KEY, self.DEFAULT)
        mock_getenv.reset_mock()

        self.assertEquals(config.get_config_path_by_env(self.KEY, default=self.DEFAULT, base_path=self.BASE_PATH),
                          self.BASE_PATH + self.DEFAULT)
        mock_getenv.assert_called_with(self.KEY, self.DEFAULT)

    @patch('os.getenv')
    def test_val_with_default(self, mock_getenv):
        mock_getenv.return_value = self.VAL
        self.assertEquals(config.get_config_path_by_env(self.KEY, default=self.DEFAULT), self.VAL)
        mock_getenv.assert_called_with(self.KEY, self.DEFAULT)
        mock_getenv.reset_mock()

        self.assertEquals(config.get_config_path_by_env(self.KEY, default=self.DEFAULT, base_path=self.BASE_PATH),
                          self.BASE_PATH + self.VAL)
        mock_getenv.assert_called_with(self.KEY, self.DEFAULT)


class _Test1:
    SOME_VAR = "some_var"

    def __init__(self):
        self._var1 = True
        self._var2 = False
        self.var3 = "var3"
        self.var4_ = [1, 2, 3]
        self.var5 = lambda x: x and True

    def test(self):
        pass


class TestConfigLoad(unittest.TestCase):
    def test_load_callable(self):
        obj = _Test1()
        expected_keys = ['var3', 'var4_', 'test', 'SOME_VAR', 'var5']

        res = list(config._load(obj, load_callable=True))
        self.assertItemsEqual(res,
                              map(lambda k: (k, getattr(obj, k)), expected_keys))

    def test_not_load_callable(self):
        obj = _Test1()
        expected_keys = ['var3', 'var4_', 'SOME_VAR']

        res = list(config._load(obj, load_callable=False))
        self.assertItemsEqual(res,
                              map(lambda k: (k, getattr(obj, k)), expected_keys))


class TestConfigFromModule(unittest.TestCase):
    NON_EXIST = 'non.existing.module'
    TEST_LIB = 'tests.lib.test_config_fixture'

    def test_not_exists(self):
        c = config.Config()
        self.assertRaises(ImportError, lambda: c.from_module(self.NON_EXIST))

    def test_exists(self):
        real_conf = import_module(self.TEST_LIB)
        real_conf_keys = filter(lambda k: not k.startswith('_'), dir(real_conf))
        real_conf_vals = dict(map(lambda k: (k, vars(real_conf).get(k)), real_conf_keys))

        c = config.Config()
        c.from_module(self.TEST_LIB)
        self.assertDictEqual(dict(c), real_conf_vals)


class TestConfigFromFile(unittest.TestCase):
    FILE_NO_PY = 'test_file.me'
    FILE_PY = 'test_file.py'

    FILE_PY_EXISTS = 'tests/lib/test_config_fixture.py'
    TEST_LIB = 'tests.lib.test_config_fixture'

    @patch('os.path.isfile')
    def test_not_exists_no_py(self, mock_isfile):
        c = config.Config()
        mock_isfile.return_value = False
        self.assertRaisesRegexp(ConfigError, '^config file does not exist at path',
                                lambda: c.from_py_file(self.FILE_NO_PY))

    @patch('os.path.isfile')
    def test_not_exists_py(self, mock_isfile):
        c = config.Config()
        mock_isfile.return_value = False
        self.assertRaisesRegexp(ConfigError, '^config file does not exist at path',
                                lambda: c.from_py_file(self.FILE_PY))

    @patch('os.path.isfile')
    def test_exists_no_py(self, mock_isfile):
        c = config.Config()
        mock_isfile.return_value = True
        self.assertRaisesRegexp(ConfigError, '^config file is not python file$',
                                lambda: c.from_py_file(self.FILE_NO_PY))

    @patch('os.path.isfile')
    def test_exists_py_fail(self, mock_isfile):
        c = config.Config()
        mock_isfile.return_value = True
        self.assertRaisesRegexp(IOError, 'Unable to load file',
                                lambda: c.from_py_file(self.FILE_PY))

    def test_exists_py(self):
        real_conf = import_module(self.TEST_LIB)
        real_conf_keys = filter(lambda k: not k.startswith('_'), dir(real_conf))

        c = config.Config()
        c.from_py_file(self.FILE_PY_EXISTS)
        self.assertItemsEqual(dict(c).keys(), real_conf_keys)


if __name__ == '__main__':
    unittest.main()

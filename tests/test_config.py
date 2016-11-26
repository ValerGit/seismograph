# -*- coding: utf-8 -*-

import unittest
from functools import update_wrapper

from mock import patch

from lib.factories import config_factory
from seismograph import config
from seismograph.exceptions import ConfigError


def compose_decorators(*decs):
    def decorator(f):
        for dec in reversed(decs):
            f = dec(update_wrapper(f, decorator))
        return f

    return decorator


# Класс как пример объекта конфигурации
class _LoadObjectForTests:
    SOME_VAR = "some_var"

    def __init__(self):
        self._var1 = True
        self._var2 = False
        self.var3 = "var3"
        self.var4_ = [1, 2, 3]
        self.var5 = lambda x: x and True

    def test(self):
        pass


LOAD_OBJECT_ALL_KEYS = ['var3', 'var4_', 'test', 'SOME_VAR', 'var5']
LOAD_OBJECT_NOT_CALLABLE_KEYS = ['var3', 'var4_', 'SOME_VAR']

FIXTURE_TEST_KEYS = ['mock', 'fixture', 'test_some_data']


class TestConfigCreateOptionParser(unittest.TestCase):
    # Можем создать OptionParser
    def test_not_none(self):
        parser = config.create_option_parser()
        self.assertIsNotNone(parser)


class TestConfigPrepareConfig(unittest.TestCase):
    # Boolean-ключи конфигурации, с которыми что-то делается после загрузки
    LOGGING_KEY = 'LOGGING_SETTINGS'
    GEVENT_KEY = 'GEVENT'
    THREADING_KEY = 'THREADING'
    ASYNC_SUITES_KEY = 'ASYNC_SUITES'
    ASYNC_TESTS_KEY = 'ASYNC_TESTS'
    MULTIPROCESSING_KEY = 'MULTIPROCESSING'
    STEPS_LOG_KEY = 'STEPS_LOG'
    FLOWS_LOG_KEY = 'FLOWS_LOG'
    VERBOSE_KEY = 'VERBOSE'

    # Можем установить настройки логирования из словарика
    @patch('logging.config.dictConfig')
    def test_logging_settings_dict(self, mock_dictConfig):
        conf_logging_dict = {
            self.LOGGING_KEY: {
                'mock': True,
            }
        }

        conf = config_factory.create(**conf_logging_dict)
        config.prepare_config(conf)
        mock_dictConfig.assert_called_with(conf_logging_dict.get(self.LOGGING_KEY))

    # Можем безопасно передать левые настройки логирования (не словарик)
    # Тогда они будут проигнорированы
    @patch('logging.config.dictConfig')
    def test_logging_settings_list(self, mock_dictConfig):
        conf_logging_not_dict = {
            self.LOGGING_KEY: [1, 2, 3],
        }

        conf = config_factory.create(**conf_logging_not_dict)
        config.prepare_config(conf)
        mock_dictConfig.assert_not_called()

    # Изменение GEVENT влияет на MULTIPROCESSING
    def test_multiprocessing_gevent(self):
        conf = {
            self.MULTIPROCESSING_KEY: False,
            self.GEVENT_KEY: False,
            self.THREADING_KEY: False,
            self.ASYNC_SUITES_KEY: True,
            self.ASYNC_TESTS_KEY: True,
        }

        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertTrue(conf_obj.get(self.MULTIPROCESSING_KEY))

        conf[self.GEVENT_KEY] = True
        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertFalse(conf_obj.get(self.MULTIPROCESSING_KEY))

    # Изменение THREADING влияет на MULTIPROCESSING
    def test_multiprocessing_threading(self):
        conf = {
            self.MULTIPROCESSING_KEY: False,
            self.GEVENT_KEY: False,
            self.THREADING_KEY: False,
            self.ASYNC_SUITES_KEY: True,
            self.ASYNC_TESTS_KEY: True,
        }

        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertTrue(conf_obj.get(self.MULTIPROCESSING_KEY))

        conf[self.THREADING_KEY] = True
        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertFalse(conf_obj.get(self.MULTIPROCESSING_KEY))

    # Изменение ASYNC_* влияет на MULTIPROCESSING
    def test_multiprocessing_async(self):
        conf = {
            self.MULTIPROCESSING_KEY: False,
            self.GEVENT_KEY: False,
            self.THREADING_KEY: False,
            self.ASYNC_SUITES_KEY: False,
            self.ASYNC_TESTS_KEY: False,
        }

        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertFalse(conf_obj.get(self.MULTIPROCESSING_KEY))

        conf[self.ASYNC_SUITES_KEY] = True
        conf[self.ASYNC_TESTS_KEY] = False
        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertTrue(conf_obj.get(self.MULTIPROCESSING_KEY))

        conf[self.ASYNC_SUITES_KEY] = False
        conf[self.ASYNC_TESTS_KEY] = True
        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertTrue(conf_obj.get(self.MULTIPROCESSING_KEY))

        conf[self.ASYNC_SUITES_KEY] = True
        conf[self.ASYNC_TESTS_KEY] = True
        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertTrue(conf_obj.get(self.MULTIPROCESSING_KEY))

    # MULTIPROCESSING без ASYNC_*, THREADING, GEVENT остается неизменным
    def test_multiprocessing_raw(self):
        conf = {
            self.MULTIPROCESSING_KEY: False,
            self.GEVENT_KEY: True,
            self.THREADING_KEY: True,
            self.ASYNC_SUITES_KEY: False,
            self.ASYNC_TESTS_KEY: False,
        }

        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertFalse(conf_obj.get(self.MULTIPROCESSING_KEY))

        conf[self.MULTIPROCESSING_KEY] = True
        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertTrue(conf_obj.get(self.MULTIPROCESSING_KEY))

    # Изменение *_LOG влияет на VERBOSE
    def test_verbose_log(self):
        conf = {
            self.VERBOSE_KEY: False,
            self.STEPS_LOG_KEY: False,
            self.FLOWS_LOG_KEY: False,
        }

        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertFalse(conf_obj.get(self.VERBOSE_KEY))

        conf[self.STEPS_LOG_KEY] = True
        conf[self.FLOWS_LOG_KEY] = False
        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertTrue(conf_obj.get(self.VERBOSE_KEY))

        conf[self.STEPS_LOG_KEY] = False
        conf[self.FLOWS_LOG_KEY] = True
        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertTrue(conf_obj.get(self.VERBOSE_KEY))

        conf[self.STEPS_LOG_KEY] = True
        conf[self.FLOWS_LOG_KEY] = True
        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertTrue(conf_obj.get(self.VERBOSE_KEY))

    # Изменение *_LOG влияет на VERBOSE
    def test_verbose_raw(self):
        conf = {
            self.VERBOSE_KEY: False,
            self.STEPS_LOG_KEY: False,
            self.FLOWS_LOG_KEY: False,
        }

        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertFalse(conf_obj.get(self.VERBOSE_KEY))

        conf[self.VERBOSE_KEY] = True
        conf_obj = config_factory.create(**conf)
        config.prepare_config(conf_obj)
        self.assertTrue(conf_obj.get(self.VERBOSE_KEY))


class TestConfigGetConfigPathByEnv(unittest.TestCase):
    KEY = "ENV_VAR_KEY"
    BASE_PATH = "BASE_PATH"
    DEFAULT = "DEFAULT"
    VAL = "VAL"

    # Можем получить путь к конфигурации из переменной окружения
    # В данном случае нет такой переменной, получаем None в любом случае
    @patch('os.getenv')
    def test_none_no_default(self, mock_getenv):
        mock_getenv.return_value = None
        self.assertEquals(config.get_config_path_by_env(self.KEY), None)
        self.assertEquals(config.get_config_path_by_env(self.KEY, base_path=self.BASE_PATH), None)

    # Можем получить путь к конфигурации из переменной окружения
    # и base path добавляется
    @patch('os.getenv')
    def test_val_no_default(self, mock_getenv):
        mock_getenv.return_value = self.VAL
        self.assertEquals(config.get_config_path_by_env(self.KEY), self.VAL)
        self.assertEquals(config.get_config_path_by_env(self.KEY, base_path=self.BASE_PATH), self.BASE_PATH + self.VAL)

    # Можем получить путь из значения по умолчанию, если его нет в переменной окружения
    # и base path добавляется
    @patch('os.getenv')
    def test_none_with_default(self, mock_getenv):
        mock_getenv.return_value = self.DEFAULT  # прихоится возвращать фолбэк
        self.assertEquals(config.get_config_path_by_env(self.KEY, default=self.DEFAULT), self.DEFAULT)
        mock_getenv.assert_called_with(self.KEY, self.DEFAULT)
        mock_getenv.reset_mock()

        self.assertEquals(config.get_config_path_by_env(self.KEY, default=self.DEFAULT, base_path=self.BASE_PATH),
                          self.BASE_PATH + self.DEFAULT)
        mock_getenv.assert_called_with(self.KEY, self.DEFAULT)

    # Можем получить путь к конфиграции из переменной окружения, значение по умолчанию игнорируется
    # и base path добавляется
    @patch('os.getenv')
    def test_val_with_default(self, mock_getenv):
        mock_getenv.return_value = self.VAL
        self.assertEquals(config.get_config_path_by_env(self.KEY, default=self.DEFAULT), self.VAL)
        mock_getenv.assert_called_with(self.KEY, self.DEFAULT)
        mock_getenv.reset_mock()

        self.assertEquals(config.get_config_path_by_env(self.KEY, default=self.DEFAULT, base_path=self.BASE_PATH),
                          self.BASE_PATH + self.VAL)
        mock_getenv.assert_called_with(self.KEY, self.DEFAULT)


class TestConfigLoad(unittest.TestCase):
    # Можем получить объект конфигурации в том числе с полями-функциями
    def test_load_callable(self):
        obj = _LoadObjectForTests()

        res = list(config._load(obj, load_callable=True))
        expected = map(lambda k: (k, getattr(obj, k)), LOAD_OBJECT_ALL_KEYS)
        self.assertItemsEqual(res, expected)

    # Можем получить объект конфигурации без полей-функций
    def test_not_load_callable(self):
        obj = _LoadObjectForTests()

        res = list(config._load(obj, load_callable=False))
        expected = map(lambda k: (k, getattr(obj, k)), LOAD_OBJECT_NOT_CALLABLE_KEYS)
        self.assertItemsEqual(res, expected)


class TestConfigFromModule(unittest.TestCase):
    NON_EXIST = 'non.existing.module'
    TEST_LIB = 'tests.lib.test_config_fixture'

    # Не можем загрузить несуществующий модуль
    def test_not_exists(self):
        c = config.Config()

        with self.assertRaises(ImportError):
            c.from_module(self.NON_EXIST)

    # Можем загрузить существующий модуль
    def test_exists(self):
        c = config.Config()
        c.from_module(self.TEST_LIB)
        self.assertItemsEqual(dict(c).keys(), FIXTURE_TEST_KEYS)


class TestConfigFromFile(unittest.TestCase):
    FILE_NO_PY = 'test_file.me'
    FILE_PY = 'test_file.py'

    FILE_PY_EXISTS = 'tests/lib/test_config_fixture.py'
    TEST_LIB = 'tests.lib.test_config_fixture'

    # Не можем загрузить несуществующий файл без .py на конце
    @patch('os.path.isfile')
    def test_not_exists_no_py(self, mock_isfile):
        c = config.Config()
        mock_isfile.return_value = False
        with self.assertRaises(ConfigError) as mock_exc:
            c.from_py_file(self.FILE_NO_PY)

        self.assertEquals(mock_exc.exception.message,
                          'config file does not exist at path "{}"'.format(self.FILE_NO_PY))

    # Не можем загрузить несуществующий файл с .py на конце
    @patch('os.path.isfile')
    def test_not_exists_py(self, mock_isfile):
        c = config.Config()
        mock_isfile.return_value = False
        with self.assertRaises(ConfigError) as mock_exc:
            c.from_py_file(self.FILE_PY)

        self.assertEquals(mock_exc.exception.message,
                          'config file does not exist at path "{}"'.format(self.FILE_PY))

    # Не можем загрузить существующий файл без .py на конце
    @patch('os.path.isfile')
    def test_exists_no_py(self, mock_isfile):
        c = config.Config()
        mock_isfile.return_value = True

        with self.assertRaises(ConfigError) as mock_exc:
            c.from_py_file(self.FILE_NO_PY)

        self.assertEquals(mock_exc.exception.message,
                          'config file is not python file')

    # Не можем загрузить существующий файл с .py на конце => можем из поймать свое исключение
    @patch('os.path.isfile')
    def test_exists_py_fail(self, mock_isfile):
        c = config.Config()
        mock_isfile.return_value = True

        with self.assertRaises(IOError) as mock_exc:
            c.from_py_file(self.FILE_PY)

        expected_start = 'Unable to load file "'
        self.assertEquals(mock_exc.exception.strerror[:len(expected_start)],
                          expected_start)

    # Можем загрузить существующий файл с .py на конце
    def test_exists_py(self):
        c = config.Config()
        c.from_py_file(self.FILE_PY_EXISTS)
        self.assertItemsEqual(dict(c).keys(), FIXTURE_TEST_KEYS)


class TestConfigInitPath(unittest.TestCase):
    PATH_IMPORT = 'some.module.for.testing'
    PATH_PY = 'some_file.py'
    PATH_NO = 'importlib'

    patch_from = compose_decorators(
        patch.object(config.Config, 'from_module'),
        patch.object(config.Config, 'from_py_file')
    )

    # Можем пытаться загрузить конфигурацию из модуля, если путь похож на модуль
    @patch_from
    def test_path_import(self, mock_from_py_file, mock_from_module):
        c = config.Config(path=self.PATH_IMPORT)
        mock_from_module.assert_called_once_with(self.PATH_IMPORT)
        mock_from_py_file.assert_not_called()

    # Можем пытаться загрузить конфигурацию из файла, если путь похож на .py файл
    @patch_from
    def test_path_py(self, mock_from_py_file, mock_from_module):
        c = config.Config(path=self.PATH_PY)
        mock_from_module.assert_not_called()
        mock_from_py_file.assert_called_once_with(self.PATH_PY)

    # Не можем загрузить конфигурацию из непонятно чего (ни файл, ни модуль)
    @patch_from
    def test_path_no(self, mock_from_py_file, mock_from_module):
        c = config.Config(path=self.PATH_NO)
        mock_from_module.assert_not_called()
        mock_from_py_file.assert_not_called()


class TestConfigInitOptions(unittest.TestCase):
    # Можем создать девственно чистый конфиг
    def test_no_options(self):
        c = config.Config(options=None)
        self.assertListEqual(dict(c).keys(), [])

    # Можем создать конфиг с полями из объекта (поля-не функции)
    def test_options(self):
        obj = _LoadObjectForTests()
        c = config.Config(options=obj)
        real_dict = dict(map(lambda k: (k, getattr(obj, k)), LOAD_OBJECT_NOT_CALLABLE_KEYS))
        self.assertDictEqual(dict(c), real_dict)


if __name__ == '__main__':
    unittest.main()

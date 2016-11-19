import unittest

from seismograph.exceptions import *


class SeismographExceptionsTestCase(unittest.TestCase):

    def setUp(self):
        self.errors = [SeismographError, Skip, LoaderError, ConfigError,
                    EmergencyStop, CollectError, PyVersionError,
                    TimeoutException, ExtensionNotFound, ExtensionNotRequired,
                    DependencyError];

    def test_Errors_message(self):
        test_message = "test error"

        for error in self.errors:
            try:
                raise error(test_message)
            except error as e:
                self.assertEqual(e.message, test_message)

    def test_Errors_no_message(self):
        for error in self.errors:
            try:
                raise error()
            except error as e:
                self.assertEqual(e.message, '')

    def test_ALLOW_RAISED_EXCEPTIONS_exists(self):
        allow_exceptions_length = len(ALLOW_RAISED_EXCEPTIONS)
        self.assertTrue(allow_exceptions_length > 0)


if __name__ == '__main__':
    unittest.main()

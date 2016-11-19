import unittest

from seismograph.exceptions import ALLOW_RAISED_EXCEPTIONS
from seismograph.exceptions import CollectError
from seismograph.exceptions import ConfigError
from seismograph.exceptions import DependencyError
from seismograph.exceptions import EmergencyStop
from seismograph.exceptions import ExtensionNotFound
from seismograph.exceptions import ExtensionNotRequired
from seismograph.exceptions import LoaderError
from seismograph.exceptions import PyVersionError
from seismograph.exceptions import SeismographError
from seismograph.exceptions import Skip
from seismograph.exceptions import TimeoutException


class SeismographExceptionsTestCase(unittest.TestCase):
    def setUp(self):
        self.errors = [SeismographError, Skip, LoaderError, ConfigError,
                       EmergencyStop, CollectError, PyVersionError,
                       TimeoutException, ExtensionNotFound, ExtensionNotRequired,
                       DependencyError]

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

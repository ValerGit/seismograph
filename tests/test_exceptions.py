# -*- coding: utf-8 -*-

import unittest

from seismograph.exceptions import SeismographError


class TestExceptions(unittest.TestCase):
    SOME_MESSAGE = "Some_message"

    def setUp(self):
        self.exception = SeismographError(self.__class__.SOME_MESSAGE)

    def tearDown(self):
        pass

    def test_message(self):
        self.assertEqual(self.exception.message, self.__class__.SOME_MESSAGE)


if __name__ == '__main__':
    unittest.main()

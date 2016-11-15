# -*- coding: utf-8 -*-

import unittest
from seismograph.datastructures import Context


class DataStructuresTestCase(unittest.TestCase):
    def setUp(self):
        self.context = Context()
        self.testItem = "TEST"

    def test_getattr_AttributeError_message(self):
        errorString = '"Context" does not have "{}" attribute.'.format(self.testItem)
        try:
            self.context.__delattr__(self.testItem)
        except AttributeError as error:
            self.assertEquals(error.message, errorString)

    def test_getattr_raise_AttributeError(self):
        self.assertRaises(AttributeError, self.context.__getattr__, self.testItem)

    def test_setattr(self):
        testValue = "hello world"
        self.context.__setattr__(self.testItem, testValue)
        self.assertEqual(self.context[self.testItem], testValue)


    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()

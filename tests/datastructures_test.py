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
        testValue = "test"
        self.context.__setattr__(self.testItem, testValue)
        self.assertEqual(self.context[self.testItem], testValue)

    def test_delattr_del(self):
        self.context[self.testItem] = "test"
        self.context.__delattr__(self.testItem)
        self.assertRaises(AttributeError, self.context.__getattr__, self.testItem)

    def test_delattr_raise_AttributeError(self):
        self.assertRaises(AttributeError, self.context.__delattr__, self.testItem)

    def test_delattr_AttributeError_message(self):
        self.context[self.testItem] = "test"
        self.context.__delattr__(self.testItem)
        self.assertRaises(AttributeError, self.context.__getattr__, self.testItem)

    def test_function_copy(self):
        self.context[0] = "test1"
        self.context[1] = "test2"

        newContext = self.context.copy()
        self.assertEquals(self.context, newContext)


if __name__ == '__main__':
    unittest.main()

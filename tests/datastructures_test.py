# -*- coding: utf-8 -*-

import unittest

from seismograph.datastructures import Context


class DataStructuresTestCase(unittest.TestCase):
    def setUp(self):
        self.context = Context()
        self.test_item = 'TEST'

    def test_getattr_attribute_error_message(self):
        with self.assertRaises(AttributeError):
            self.context.__delattr__(self.test_item)

    def test_getattr_raise_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.context.__getattr__(self.test_item)

    def test_setattr(self):
        test_value = 'test'
        self.context.__setattr__(self.test_item, test_value)
        self.assertEqual(self.context[self.test_item], test_value)

    def test_delattr_del(self):
        self.context[self.test_item] = 'test'
        self.context.__delattr__(self.test_item)

        with self.assertRaises(AttributeError):
            self.context.__getattr__(self.test_item)

    def test_delattr_raise_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.context.__delattr__(self.test_item)

    def test_delattr_attribute_error_message(self):
        self.context[self.test_item] = 'test'
        self.context.__delattr__(self.test_item)

        with self.assertRaises(AttributeError):
            self.context.__getattr__(self.test_item)

    def test_function_copy(self):
        self.context.update({
            'Hello': 'dear tester',
            'Cool': 'tests for everyone'
        })
        new_context = self.context.copy()
        self.assertEquals(self.context, new_context)


if __name__ == '__main__':
    unittest.main()

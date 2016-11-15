# -*- coding: utf-8 -*-

import unittest
from seismograph.datastructures import Context


class DataStructuresTestCase(unittest.TestCase):
    def setUp(self):
        self.context = Context()
        self.testItem = 0


    def tearDown(self):
        pass

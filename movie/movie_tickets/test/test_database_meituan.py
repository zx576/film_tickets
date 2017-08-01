# coding=utf-8
# author = zhouxin
# date = 2017.7.4

import unittest

from database.meituan_dt import MeiTuan_Dt

class TestMeituan_Dt(unittest.TestCase):

    def setUp(self):
        self.mt = MeiTuan_Dt()

    def tearDown(self):
        pass

    def test_insert(self):
        pass
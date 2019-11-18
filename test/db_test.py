import os
import unittest
from beacons_server.db import DB


class DBTest(unittest.TestCase):

    def setUp(self):
        self.db = DB('test_db.sqlite')
        self.db.SILENT = True
        self.db.create_tables()


    def tearDown(self):
        os.remove("test_db.sqlite")


    def test_tables_exist(self):
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        res = self.db.select(sql)
        self.assertEqual(len(res), 5)


    def test_insert_object(self):
        self.assertEqual(self.db.insert_object('bookmark', {'name':'John'}), 1)


    def test_format_and_condition(self):
        self.assertEqual(self.db._format_and_condition(), '')
        self.assertEqual(self.db._format_and_condition(id=2, name='John'),
                         'WHERE id = ? AND name = ?')


    def test_format_order_by(self):
        self.assertEqual(self.db._format_order_by(''), '')
        self.assertEqual(self.db._format_order_by('position'),
                         'ORDER BY position')
        self.assertEqual(self.db._format_order_by(['id', 'position']),
                         'ORDER BY id, position')


    def test_select_table(self):
        self.db.insert_object('bookmark', {'name':'John'})
        self.assertEqual(self.db.select_table('bookmark', name='Doe'), [])
        # self.assertEqual(self.db.select_table('bookmark', name='John'), {'name':'John'})

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
        res = self.db.select_sql(sql)
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


    def test_select(self):
        id1 = self.db.insert_object('bookmark', {'name':'John', 'position':2})
        id2 = self.db.insert_object('bookmark', {'name':'Doe', 'position':1})

        self.assertEqual(self.db.select('bookmark', name='Bob'), [])
        self.assertIsNone(self.db.select('bookmark', unique=True, name='Bob'))

        self.assertEqual(len(self.db.select('bookmark', name='John')), 1)
        self.assertIsInstance(self.db.select('bookmark', unique=True, name='John'), dict)
        self.assertIs(self.db.select('bookmark', unique=True, name='John')['id'], id1)

        items = self.db.select('bookmark', orderBy='position')
        self.assertEqual(items[0]['position'], 1)
        self.assertEqual(items[1]['position'], 2)

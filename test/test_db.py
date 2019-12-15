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
        self.assertEqual(self.db.insert_object('bookmark', {}), 1)
        self.assertEqual(self.db.insert_object('bookmark', {'name':'John'}), 2)
        self.assertEqual(self.db.insert_object('bookmark', {'inexistentTable':'John'}), None)


    def test_insert_generated_position(self):
        # Without parent defined
        id1 = self.db.insert_object('bookmark', {'position': None})
        id2 = self.db.insert_object('bookmark', {'position': None})
        self.assertEqual(self.db.select('bookmark', unique=True, id=id1)['position'], 0)
        self.assertEqual(self.db.select('bookmark', unique=True, id=id2)['position'], 1)

        # With parent defined
        id3 = self.db.insert_object('bookmark', {'parent_id':1, 'position':None})
        id4 = self.db.insert_object('bookmark', {'parent_id':1, 'position':None})
        self.assertEqual(self.db.select('bookmark', unique=True, id=id3)['position'], 0)
        self.assertEqual(self.db.select('bookmark', unique=True, id=id4)['position'], 1)


    def test_format_fields_values(self):
        self.assertEqual(self.db._format_fields_values(), '')
        self.assertEqual(self.db._format_fields_values('id'),
                         ['id = ?'])
        self.assertEqual(self.db._format_fields_values('id', 'name'),
                         ['id = ?', 'name = ?'])


    def test_get_sql_args(self):
        # Test without argument
        self.assertEqual(self.db._get_sql_args(), ({}, {}))

        # Test with None value
        self.assertEqual(self.db._get_sql_args(none_value=None), ({}, {}))

        # Test with WHERE arguments using a dictionnary
        self.assertEqual(self.db._get_sql_args({'id':1}), ({'id':1}, {}))
        self.assertEqual(self.db._get_sql_args({'id':1,'name':'John'}), ({'id':1,'name':'John'}, {}))

        # Test with SQL arguments using a dictionnary
        self.assertEqual(self.db._get_sql_args({'_limit':5}), ({}, {'_limit':5}))
        self.assertEqual(self.db._get_sql_args({'_order by':'id','_limit':5}), ({}, {'_limit':5, '_order by':'id'}))

        # Test with WHERE + SQL arguments using a dictionnary
        self.assertEqual(self.db._get_sql_args({'id':1, '_limit':5}), ({'id':1}, {'_limit':5}))

        # Test with WHERE + SQL arguments using named arguments
        self.assertEqual(self.db._get_sql_args(id=1, _limit=5), ({'id':1}, {'_limit':5}))

        # Test with WHERE + SQL arguments using both a dictionnary and named arguments
        self.assertEqual(self.db._get_sql_args(id=1, _limit=5, args={'name':'John', '_order by':'id'}), ({'id':1, 'name':'John'}, {'_limit':5, '_order by':'id'}))

        # Test with WHERE + SQL arguments using both a dictionnary and named arguments with None values
        self.assertEqual(self.db._get_sql_args(id=1, _limit=None, args={'name':None, '_order by':'id'}), ({'id':1}, {'_order by':'id'}))


    def test_format_and_condition(self):
        self.assertEqual(self.db._format_and_condition(), '')
        self.assertEqual(self.db._format_and_condition('id'), 'WHERE id = ?')
        self.assertEqual(self.db._format_and_condition('id', 'name'),
                         'WHERE id = ? AND name = ?')


    def test_format_sql_args(self):
        self.assertEqual(self.db._format_sql_args(), '')
        self.assertEqual(self.db._format_sql_args({'limit':5}), 'LIMIT 5')
        self.assertEqual(self.db._format_sql_args({'limit':5, 'nonevalue':None}), 'LIMIT 5')
        self.assertEqual(self.db._format_sql_args({'order by':'id', 'limit':5}), 'ORDER BY id LIMIT 5')
        self.assertEqual(self.db._format_sql_args({'order_by':'id', 'limit':5}), 'ORDER BY id LIMIT 5')
        self.assertEqual(self.db._format_sql_args({'order_by':'id', 'asc':True}), 'ORDER BY id ASC')
        self.assertEqual(self.db._format_sql_args({'order_by':'id', 'desc':True}), 'ORDER BY id DESC')


    def test_select(self):
        id1 = self.db.insert_object('bookmark', {'name':'John', 'position':2})
        id2 = self.db.insert_object('bookmark', {'name':'Doe', 'position':1})

        self.assertEqual(self.db.select('bookmark', name='Bob'), [])
        self.assertIsNone(self.db.select('bookmark', unique=True, name='Bob'))

        self.assertEqual(len(self.db.select('bookmark', name='John')), 1)
        self.assertIsInstance(self.db.select('bookmark', unique=True, name='John'), dict)
        self.assertIs(self.db.select('bookmark', unique=True, name='John')['id'], id1)

        items = self.db.select('bookmark', _order_by='position')
        self.assertEqual(items[0]['position'], 1)
        self.assertEqual(items[1]['position'], 2)

        # Testing key words arguments search
        items = self.db.select('bookmark', position=1)
        self.assertEqual(items[0]['position'], 1)
        self.assertEqual(len(items), 1)

        # Testing dictionnary argument search
        items = self.db.select('bookmark', args={'position':1})
        self.assertEqual(items[0]['position'], 1)
        self.assertEqual(len(items), 1)


    def test_update_item(self):
        id = self.db.insert_object('bookmark', {'name':'John', 'position':1})

        item = self.db.select('bookmark', id = id)
        self.assertEqual(item[0]['position'], 1)

        # Testing with 0 argument
        self.db.update_item('bookmark', id)
        item = self.db.select('bookmark', id = id)
        self.assertEqual(item[0]['name'], 'John')
        self.assertEqual(item[0]['position'], 1)

        # Testing with 1 argument
        self.db.update_item('bookmark', id, position=2)
        item = self.db.select('bookmark', id = id)
        self.assertEqual(item[0]['position'], 2)

        # Testing with 2 arguments
        self.db.update_item('bookmark', id, name='Doe', position=3)
        item = self.db.select('bookmark', id = id)
        self.assertEqual(item[0]['name'], 'Doe')
        self.assertEqual(item[0]['position'], 3)


    def test_select_items_to_move(self):
        id1 = self.db.insert_object('bookmark', {'name':'Joh', 'position':1, 'parent_id':1})
        id2 = self.db.insert_object('bookmark', {'name':'Doe', 'position':2, 'parent_id':1})
        id3 = self.db.insert_object('bookmark', {'name':'Bob', 'position':3, 'parent_id':1})
        id4 = self.db.insert_object('bookmark', {'name':'Foo', 'position':4, 'parent_id':1})
        id5 = self.db.insert_object('bookmark', {'name':'Olf', 'position':1, 'parent_id':2})

        items_to_move = self.db._select_items_to_move('bookmark', min_position = 1, parent_id = 1)
        self.assertEqual(len(items_to_move), 4)

        items_to_move = self.db._select_items_to_move('bookmark', min_position = 2, max_position = 4, parent_id = 1)
        self.assertEqual(len(items_to_move), 3)

        items_to_move = self.db._select_items_to_move('bookmark', min_position = 2, parent_id = 2)
        self.assertEqual(len(items_to_move), 0)


    def test_reposition_items(self):
        id1 = self.db.insert_object('bookmark', {'name':'Joh', 'position':1, 'parent_id':1})
        id2 = self.db.insert_object('bookmark', {'name':'Doe', 'position':2, 'parent_id':1})
        id3 = self.db.insert_object('bookmark', {'name':'Bob', 'position':3, 'parent_id':1})
        id4 = self.db.insert_object('bookmark', {'name':'Foo', 'position':4, 'parent_id':1})
        id5 = self.db.insert_object('bookmark', {'name':'Olf', 'position':1, 'parent_id':2})

        # Move up all items
        self.db._reposition_items('bookmark', direction = 'up', min_position = 1, parent_id = 1)
        items_moved = self.db._select_items_to_move('bookmark', min_position = 0, parent_id = 1)
        for index, item in enumerate(items_moved):
            self.assertEqual(item['position'], index)
        items = self.db.select('bookmark', parent_id = 2)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['position'], 1)

        # Move down all items
        self.db._reposition_items('bookmark', direction = 'down', min_position = 0, parent_id = 1)
        items_moved = self.db._select_items_to_move('bookmark', min_position = 0, parent_id = 1)
        for index, item in enumerate(items_moved):
            self.assertEqual(item['position'], index + 1)

        # Move down items from 1 to 3
        self.db._reposition_items('bookmark', direction = 'up', min_position = 1, max_position = 3, parent_id = 1)
        items_moved = self.db._select_items_to_move('bookmark', min_position = 0, max_position = 3, parent_id = 1)
        for index, item in enumerate(items_moved):
            self.assertEqual(item['position'], index)
        items = self.db.select('bookmark', position = 4)
        self.assertEqual(len(items), 1)


    def test_delete_item(self):
        id = self.db.insert_object('bookmark', {'name':'Joh'})
        self.assertIsNotNone(self.db.select('bookmark', unique=True, id=id))
        self.db._delete_item('bookmark', id)
        self.assertIsNone(self.db.select('bookmark', unique=True, id=id))


    def test_remove_item(self):
        id1 = self.db.insert_object('bookmark', {'name':'Joh', 'position':1, 'parent_id':1})
        id2 = self.db.insert_object('bookmark', {'name':'Doe', 'position':2, 'parent_id':1})
        id3 = self.db.insert_object('bookmark', {'name':'Bob', 'position':3, 'parent_id':1})
        id4 = self.db.insert_object('bookmark', {'name':'Foo', 'position':4, 'parent_id':1})
        id5 = self.db.insert_object('bookmark', {'name':'Olf', 'position':1, 'parent_id':2})

        self.db.remove_item('bookmark', id2)

        items = self.db.select('bookmark', _order_by='position', parent_id=1)
        self.assertEqual(items[0]['position'], 1)
        self.assertEqual(items[1]['position'], 2)
        self.assertEqual(items[2]['position'], 3)

        self.assertEqual(self.db.select('bookmark', unique=True, parent_id=2)['position'], 1)


    def test_get_child_table(self):
        self.assertIsNone(self.db._get_child_table('bookmark'))
        self.assertEqual(self.db._get_child_table('slide'), 'row')
        self.assertEqual(self.db._get_child_table('box'), 'bookmark')

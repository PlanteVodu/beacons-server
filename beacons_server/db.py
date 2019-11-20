#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

class DB:

    # Describe the structure of the data base objects
    OBJ_TYPES = ['slide', 'row', 'column', 'box', 'bookmark']
    SQL_TABLES = {
        'slide': """CREATE TABLE IF NOT EXISTS slide (
            id integer PRIMARY KEY,
            position integer,
            name text
        );""",

        'row': """CREATE TABLE IF NOT EXISTS row (
            id integer PRIMARY KEY,
            parent_id integer,
            position integer,
            name text,
            css text,
            FOREIGN KEY (parent_id) REFERENCES slide (id)
        );""",

        'column': """CREATE TABLE IF NOT EXISTS column (
            id integer PRIMARY KEY,
            parent_id integer,
            position integer,
            name text,
            FOREIGN KEY (parent_id) REFERENCES row (id)
        );""",

        'box': """CREATE TABLE IF NOT EXISTS box (
            id integer PRIMARY KEY,
            parent_id integer,
            position integer,
            name text,
            FOREIGN KEY (parent_id) REFERENCES column (id)
        );""",

        'bookmark': """CREATE TABLE IF NOT EXISTS bookmark (
            id integer PRIMARY KEY,
            parent_id integer,
            position integer,
            name text,
            icon text,
            url text,
            FOREIGN KEY (parent_id) REFERENCES box (id)
        );""",
    }


    def __init__(self, db_path, silent=False):
        """Initialize the connection with the SQLite data base file."""
        self.conn = self._create_connection(db_path)
        self.SILENT = silent
        if create_tables:
            self.create_tables()
        self._set_tables_data()


    def _set_tables_data(self):
        self.data = {table: self._get_sorted_table_items(table) for table in DB.OBJ_TYPES}


    def _get_sorted_table_items(self, table):
        items = self.select(table, orderBy='id')
        return {item['id']: item for item in items}


    def _update_item_data(self, table, id):
        item = self.select(table, id=id, unique=True)
        if item != None:
            self.data[table][id] = item
        return item


    def _remove_item_data(self, table, id):
        self.data[table].pop(id, None)


    def __del__(self):
        """End the SQLite data base connection."""
        self.conn.close()


    def _create_connection(self, path):
        """Create a database connection to a SQLite database."""
        try:
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            conn.text_factory = str
            return conn
        except sqlite3.Error as exception:
            raise SystemError("Could not establish a connection with the database '{}'. Error message: {}".format(path, exception))

        return None


    def execute_sql(self, sql, data = None):
        """Execute an SQL request along with data, if any."""
        try:
            if not self.SILENT:
                print('   * %s: %s' % (Fore.CYAN + 'sql' + Style.RESET_ALL, sql))
            cur = self.conn.cursor()
            if data is None:
                cur.execute(sql)
            else:
                if not self.SILENT:
                    print('   * %s: %s' % (Fore.CYAN + 'data' + Style.RESET_ALL, str(data)))
                cur.execute(sql, data)
            self.conn.commit()
            return cur
        except sqlite3.Error as e:
            print(e)


    def create_tables(self):
        """Create default tables."""
        if not self.SILENT:
            print('Create tables...')
        for name in self.SQL_TABLES.keys():
            self.execute_sql(self.SQL_TABLES[name])


    def insert_object(self, table, obj):
        """Insert an object represented as a dictionnary inside a table.
        Return the id of the row created."""
        if len(list(obj.values())) == 0:
            sql = 'INSERT INTO %s DEFAULT VALUES' % table
            values = None
        else:
            fields = '(%s)' % ','.join(obj.keys())

            values = ['?' for i in range(len(obj.keys()))]
            values = '(%s)' % ','.join(values)

            sql = 'INSERT INTO %s %s VALUES %s' % (table, fields, values)

        cur = self.execute_sql(sql, tuple(obj.values()))

        id = cur.lastrowid
        return self._update_item_data(table, cur.lastrowid)


    def select_sql(self, sql, obj=None, unique=False):
        """Execute an SQL request and return the objects selected as a list of
        dictionnaries. Return an empty list if no object where found.
        If 'unique' is True, return the object itself if it exists or None."""
        cur = self.execute_sql(sql=sql, data=obj)
        if cur == None:
            print('select_sql: cur is None! Actually this condition is useful! :)')
            print(sql)
            print(obj)
            if unique:
                return None
            return []
        res = [dict(row) for row in cur.fetchall()]
        if unique:
            if len(res) > 0:
                return res[0]
            return None
        return res


    def select(self, table, orderBy='', unique=False, **kwargs):
        """Apply a SELECT request on a table. It can specify an AND
        condition using named arguments and an ORDER BY.
        If 'unique' is True, return the object itself if it exists or None."""
        where = self._format_and_condition(*kwargs.keys())
        orderBy = self._format_order_by(orderBy)

        sql = "SELECT * FROM %s %s %s" % (table, where, orderBy)
        data = tuple(kwargs.values())

        return self.select_sql(sql, data, unique)


    def _format_fields_values(self, *args):
        """Return an array of strings, each string being in the form
        'field = ?'."""
        if len(args) == 0:
            return ''
        return ['%s = ?' % field for field in args]


    def _format_and_condition(self, *args):
        """Return a WHERE condition with every named argument received
        using an AND condition."""
        if len(args) == 0:
            return ''
        fields_values = self._format_fields_values(*args)
        return 'WHERE ' + ' AND '.join(fields_values)


    def _format_order_by(self, orderBy=''):
        """Return an ORDER BY formated with either a string or a list."""
        if len(orderBy) == 0:
            return ''
        if type(orderBy) is list:
            orderBy = ', '.join(orderBy)

        return 'ORDER BY %s' % orderBy


    def update_item(self, table, id, **kwargs):
        """Update the specified item's fields with the given values."""
        if len(kwargs) == 0:
            return
        fields_values = ', '.join(self._format_fields_values(*kwargs.keys()))
        sql = 'UPDATE %s SET %s WHERE id = ?' % (table, fields_values)
        data = tuple(kwargs.values()) + (id,)
        self.execute_sql(sql, data)

        return self._update_item_data(table, id)


    def move_item(self, table, id, new_position, parent_id = None):
        """Change an item's position and parent and update the affected
        items so that every item's positions remain consecutive.

        If only the item's position is modified, the affected items are
        moved up or down accordingly.

        If the item's parent is changed, the positions of the items from
        both old and new parents are updated as follows :
        - move up (position-1) the old following items (from the old parent)
        - move down (position+1) the new following items (from the new
        parent)"""
        item = self.select(table, unique = True, id = id)
        if item is None:
            return None
        if 'parent_id' in item and parent_id != None and item['parent_id'] != parent_id:
            # Update affected items from both old and new parents
            # Move up the old parent's items from old_position+1 to last
            self._reposition_items(table, direction='up', min_position=item['position']+1, parent_id=item['parent_id'])
            # Move down the new parent's items from new_position to last
            self._reposition_items(table, direction='up', min_position=new_position, parent_id=parent_id)

            self.update_item(table, id, parent=parent_id)
            self.update_item(table, id, position=new_position)
        elif item['position'] != new_position:
            if item['position'] < new_position: # move item up
                # Move down items from new_position to old_position-1
                self._reposition_items(table, direction='down', min_position=new_position, max_position=item['position']-1)
            else: # move item down
                # Move up items from old_position+1 to new_position
                self._reposition_items(table, direction='up', min_position=item['position']+1, max_position=new_position)

            self.update_item(table, id, position=new_position)

        return self._update_item_data(table, id)


    def _reposition_items(self, table, direction, min_position, max_position = None, parent_id = None):
        """Increase or decrease a range of items' position."""
        items_to_move = self._select_items_to_move(table = table, min_position = min_position, max_position = max_position, parent_id = parent_id)

        amount = -1 if direction == 'up' else +1

        for item in items_to_move:
            new_position = item['position'] + amount
            self.update_item(table, item['id'], position=new_position)


    def _select_items_to_move(self, table, min_position, max_position = None, parent_id = None):
        """Return items inside a range of positions having the given parent."""
        sql = 'SELECT * FROM %s WHERE position >= ?' % table
        data = (min_position,)

        if max_position is not None:
            sql += ' AND position <= ?'
            data = data + (max_position,)

        if parent_id is not None:
            sql += ' AND parent_id = ?'
            data = data + (parent_id,)

        return self.select_sql(sql, data)


    def remove_item(self, table, id):
        """Remove the specified item and move up it's following items."""
        item = self.select(table, unique = True, id = id)
        if item is None:
            return
        if 'parent_id' in item:
            self._reposition_items(table, direction='up', min_position=item['position']+1, parent_id=item['parent_id'])
        self._delete_item(table, id)


    def _delete_item(self, table, id):
        """Delete the specified item from the database."""
        sql = 'DELETE FROM %s WHERE id = ?' % table
        data = (id,)
        self.execute_sql(sql, data)
        self._remove_item_data(table, id)


    def get_items_with_descendants(self, table, parent_id = None):
        """Return items with the specified parent along with all
        their descendants (childs, grand-childs, etc.)."""
        if parent_id is None:
            items = self.select(table, orderBy='position')
        else:
            items = self.select(table, orderBy='position', parent_id=parent_id)

        type_index = self.OBJ_TYPES.index(table)
        if type_index == len(self.OBJ_TYPES) - 1:
            return items

        childs_table = self.OBJ_TYPES[type_index+1]
        for i, item in enumerate(items):
            items[i]['content'] = self.get_items_with_descendants(childs_table, item['id'])

        return items

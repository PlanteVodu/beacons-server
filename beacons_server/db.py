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


    def __init__(self, db_path):
        """Initialize the connection with the SQLite data base file."""
        self.conn = self._create_connection(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.text_factory = str
        self.SILENT = False


    def __del__(self):
        """End the SQLite data base connection."""
        self.conn.close()


    def _create_connection(self, path):
        """Create a database connection to a SQLite database."""
        try:
            conn = sqlite3.connect(path)
            return conn
        except sqlite3.Error as e:
            print(e)

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

        cur = self.execute_sql(sql, list(obj.values()))
        return cur.lastrowid


    def select_sql(self, sql, obj=None, unique=False):
        """Execute an SQL request and return the objects selected as a list of
        dictionnaries. Return an empty list if no object where found.
        If 'unique' is True, return the object itself if it exists or None."""
        cur = self.execute_sql(sql=sql, data=obj)
        if cur == None:
            print('select_sql: cur is None! Actually this condition is useful! :)')
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
        where = self._format_and_condition(**kwargs)
        orderBy = self._format_order_by(orderBy)

        sql = "SELECT * FROM %s %s %s" % (table, where, orderBy)

        return self.select_sql(sql, list(kwargs.values()), unique)


    def _format_and_condition(self, **kwargs):
        """Return a WHERE condition with every named argument received
        using an AND condition."""
        if len(kwargs) == 0:
            return ''

        conditions = [f'{key} = ?' for key in kwargs.keys()]
        where = 'WHERE ' + ' AND '.join(conditions)

        return where


    def _format_order_by(self, orderBy=''):
        """Return an ORDER BY formated with either a string or a list."""
        if len(orderBy) == 0:
            return ''

        if type(orderBy) is list:
            orderBy = ', '.join(orderBy)

        return 'ORDER BY %s' % orderBy


    def _update_item_parent(self, table, id, new_parent_id):
        """Update an item's parent inside the database."""
        sql = 'UPDATE %s SET parent_id = ? WHERE id = ?' % table
        data = (new_parent_id, id,)
        self.execute_sql(sql, data)


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
            return
        if 'parent_id' in item and parent_id != None and item['parent_id'] != parent_id:
            # Update affected items from both old and new parents
            # Move up the old parent's items from old_position+1 to last
            self.reposition_items(table, direction='up', min_position=item['position']+1, parent_id=item['parent_id'])
            # Move down the new parent's items from new_position to last
            self.reposition_items(table, direction='up', min_position=new_position, parent_id=parent_id)

            self.update_item_position(table, id, new_position)
            self._update_item_parent(table, id, parent_id)
        elif item['position'] != new_position:
            if item['position'] < new_position: # move item up
                # Move down items from new_position to old_position-1
                self.reposition_items(table, direction='down', min_position=new_position, max_position=item['position']-1)
            else: # move item down
                # Move up items from old_position+1 to new_position
                self.reposition_items(table, direction='up', min_position=item['position']+1, max_position=new_position)

            self.update_item_position(table, id, new_position)


    def update_item_position(self, table, id, new_position):
        """Update an item's position inside the database."""
        sql = 'UPDATE %s SET position = ? WHERE id = ?' % table
        data = (new_position, id,)
        self.execute_sql(sql, data)


    def reposition_items(self, table, direction, min_position, max_position = None, parent_id = None):
        """Increase or decrease a range of items' position."""
        items_to_move = self._select_items_to_move(table = table, min_position = min_position, max_position = max_position, parent_id = parent_id)

        amount = -1 if direction == 'up' else +1

        for item in items_to_move:
            new_position = item['position'] + amount
            self.update_item_position(table, item['id'], new_position)


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

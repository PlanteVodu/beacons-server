#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

class DB:

    SQL_COMMANDS_ORDER = ['GROUP BY', 'ORDER BY', 'ASC', 'DESC', 'LIMIT']
    SQL_COMMANDS_WITHOUT_ARGUMENT = ['ASC', 'DESC']

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


    def __init__(self, db_path, create_tables=False, silent=False):
        """Initialize the connection with the SQLite data base file."""
        self.conn = self._create_connection(db_path)
        self.SILENT = silent
        if create_tables:
            self.create_tables()


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
            values = ()
        else:
            # Ignore SQL commands
            obj = {k:v for k,v in obj.items() if k[0] != '_'}

            fields = '(%s)' % ','.join(obj.keys())

            values = ['?' for i in range(len(obj.keys()))]
            values = '(%s)' % ','.join(values)

            sql = 'INSERT INTO %s %s VALUES %s' % (table, fields, values)

        # Generate 'position' attribute if not set
        if 'position' in obj and obj['position'] is None:
            if 'parent_id' in obj and obj['parent_id'] != None:
                position = len(self.select(table, parent_id=obj['parent_id']))
            else:
                position = len(self.select(table))
            obj['position'] = position

        data = tuple(obj.values())

        cur = self.execute_sql(sql, data)
        if cur != None:
            return cur.lastrowid
        return None


    def select_sql(self, sql, obj=None, unique=False):
        """Execute an SQL request and return the objects selected as a list of
        dictionnaries. Return an empty list if no object where found.
        If 'unique' is True, return the object itself if it exists or None."""
        cur = self.execute_sql(sql=sql, data=obj)
        if cur == None:
            if unique:
                return None
            return []
        res = [dict(row) for row in cur.fetchall()]
        if unique:
            if len(res) > 0:
                return res[0]
            return None
        return res


    def select(self, table, orderBy='', unique=False, args = {}, **kwargs):
        """Apply a SELECT request on a table. It can specify an AND
        condition using named arguments and an ORDER BY.
        If 'unique' is True, return the object itself if it exists or None."""
        where_args, sql_args = self._get_sql_args(args, **kwargs)

        where = self._format_and_condition(*where_args.keys())
        sql_commands = self._format_sql_args(sql_args)

        sql = "SELECT * FROM %s %s %s" % (table, where, sql_commands)
        data = tuple(where_args.values())

        return self.select_sql(sql, data, unique)


    def _get_sql_args(self, args = {}, **kwargs):
        """Return received arguments splitted into two sets representing WHERE
        arguments and SQL commands arguments. Sets are made according to the
        arguments keys :
        - SQL arguments' key starts with a '_' ; key is set in uppercase ;
        - Every other argument goes inside the WHERE set.
        Arguments with None values are ignored.
        """
        # Merge the two sets of args
        args = {**args, **kwargs}
        # Remove arguments' None values
        args = {k:v for k,v in args.items() if v is not None}

        # Get the SQL request's arguments
        sql_keys = [k for k in args.keys() if k[0] == '_']
        sql_args = {k:v for k,v in args.items() if k in sql_keys}

        # Get the WHERE args by getting the difference with sql_args
        where_keys = set(args.keys()).difference(sql_keys)
        where_args = {k:v for k,v in args.items() if k in where_keys}

        return where_args, sql_args


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


    def _format_sql_args(self, args = {}):
        """Return formated SQL arguments as a string.
        Keys are uppercased and '_' are replaced with spaces, then trimmed.
        Values can be either a unique value or a list. None values are ignored.
        This function also handles commands without arguments like ASC or DESC."""
        format_sql_key = lambda k: k.upper().replace('_', ' ').strip()

        # Format args' keys into SQL commands
        args = {format_sql_key(k):v for k,v in args.items()}

        commands = []
        # We iterate over actual SQL commands to filter arguments but also to
        # sort commands in order to form a consistent SQL request.
        for key in DB.SQL_COMMANDS_ORDER:
            if key not in args or args[key] is None:
                continue
            if key in DB.SQL_COMMANDS_WITHOUT_ARGUMENT:
                commands.append(key)
            else:
                value = args[key]
                if isinstance(value, list):
                    value = ', '.join(value)
                commands.append('%s %s' % (key, value))

        return ' '.join(commands)


    def update_item(self, table, id, args = {}, **kwargs):
        """Update the specified item's fields with the given values."""
        if len(kwargs) > 0:
            args = kwargs
        elif len(args) == 0:
            return
        args = {k:v for k,v in args.items() if k[0] != '_' and v != None}
        fields_values = ', '.join(self._format_fields_values(*args.keys()))
        data = tuple(args.values()) + (id,)
        sql = 'UPDATE %s SET %s WHERE id = ?' % (table, fields_values)
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
            self._reposition_items(table, direction='up', min_position=item['position']+1, parent_id=item['parent_id'])
            # Move down the new parent's items from new_position to last
            self._reposition_items(table, direction='up', min_position=new_position, parent_id=parent_id)

            self.update_item(table, id, position=new_position)
            self.update_item(table, id, parent=parent_id)
        elif item['position'] != new_position:
            if item['position'] < new_position: # move item up
                # Move down items from new_position to old_position-1
                self._reposition_items(table, direction='down', min_position=new_position, max_position=item['position']-1)
            else: # move item down
                # Move up items from old_position+1 to new_position
                self._reposition_items(table, direction='up', min_position=item['position']+1, max_position=new_position)

            self.update_item(table, id, position=new_position)


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
        item = self.select(table, unique=True, id=id)
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


    def get_items_with_descendants(self, table, parent_id = None, until = ''):
        """Return items with the specified parent along with all
        their descendants (childs, grand-childs, etc.)."""
        if parent_id is None:
            items = self.select(table, orderBy='position')
        else:
            items = self.select(table, orderBy='position', parent_id=parent_id)

        child_table = self._get_child_table(table)
        if until == table or child_table is None:
            return items

        for i, item in enumerate(items):
            items[i]['content'] = self.get_items_with_descendants(childs_table, item['id'], until=until)

        return items


    def _get_child_table(self, table):
        return self._get_table_by_index(self.OBJ_TYPES.index(table) + 1)


    def _get_table_by_index(self, index):
        if index < 0 or index >= len(self.OBJ_TYPES):
            return None
        return self.OBJ_TYPES[index]

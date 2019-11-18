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


    def select_sql(self, sql, obj=None):
        """Execute an SQL request and return the objects selected as a list of
        dictionnaries. Return an empty list if no object where found."""
        cur = self.execute_sql(sql=sql, data=obj)
        if cur == None:
            return []
        return [dict(row) for row in cur.fetchall()]


    def select(self, table, orderBy='', **kwargs):
        """Apply a SELECT request on a table. It can specify an AND
        condition using named arguments and an ORDER BY."""
        where = self._format_and_condition(**kwargs)
        orderBy = self._format_order_by(orderBy)

        sql = "SELECT * FROM %s %s %s" % (table, where, orderBy)

        return self.select_sql(sql, list(kwargs.values()))


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

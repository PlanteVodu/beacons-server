#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import colorama
from colorama import Fore, Back, Style

from beacons_server.db import DB


colorama.init(autoreset=True)


def migrate_obj_type(db1, db2, type_index, parent_ids = None):
    table = DB.OBJ_TYPES[type_index]
    print('Migrating ' + Fore.BLUE + table + Style.RESET_ALL)

    items = db1.select(table, orderBy='id')
    ids = {}

    # Retrieve item's 'position' and 'parent_id' fields
    # from db1's 'parent_child' table.
    if type_index > 0:
        parent_type = DB.OBJ_TYPES[type_index - 1]
        parent_child_table = f'{parent_type}_{table}'
        id_field = f'{table}_id'
        parent_id_field = f'{parent_type}_id'

        for item in items:
            sql = 'SELECT * FROM %s WHERE %s = ?' % (parent_child_table, id_field)
            data = (item['id'],)
            row = db1.select_sql(sql, data, unique=True)
            if row != None:
                item['position'] = row['position']
                item['parent_id'] = row[parent_id_field]

    # Add items inside the next db
    for item in items:
        # Check if item's parent exists
        if type_index > 0:
            if 'parent_id' not in item or item['parent_id'] is None:
                # print(item['parent_id'])
                print(Fore.YELLOW + 'Warning: ' + Style.RESET_ALL + 'the following item has no parent')
                print(item)
                continue
            if item['parent_id'] not in parent_ids:
                print(Fore.YELLOW + 'Warning: ' + Style.RESET_ALL + "the parent of the following item doesn't exist")
                print(item)
                continue
            item['parent_id'] = parent_ids[item['parent_id']]

        if item['id'] > 50:
            db2.SILENT = True

        old_id = item['id']

        # Rename keys
        if 'title' in item:
            item['name'] = item.pop('title')

        # Remove unecessary attributes
        del item['id']
        if type_index == 0:
            del item['css']

        new_id = db2.insert_object(table, item)

        ids[old_id] = new_id

    return ids


if __name__ == '__main__':
    db1 = DB('beacons.db', silent=True)

    os.remove('beacons.sqlite')
    db2 = DB('beacons.sqlite', create_tables=True, silent=True)

    ids = None

    for i in range(len(DB.OBJ_TYPES)):
        if i == 4:
            db2.SILENT = False
        ids = migrate_obj_type(db1, db2, i, parent_ids=ids)
        db2.SILENT = True
        # if i == 3:
        #     print(ids)
        #     break

import sys
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_restful import reqparse, abort, Api, Resource
import colorama
from colorama import Fore, Back, Style

from beacons_server import db

colorama.init(autoreset=True)

app = Flask(
    __name__,
    static_folder = '',
    static_url_path = '',
    template_folder = ''
)
api = Api(app)

CORS(app, resources={r'/*': {'origins': '*'}})

general_parser = reqparse.RequestParser()
general_parser.add_argument('id', type=int)
# general_parser.add_argument('id', type=int)
general_parser.add_argument('title', default='', trim=True)
general_parser.add_argument('position', type=int, required=True, help='Element must specify a position')

child_parser = general_parser.copy()
child_parser.add_argument('parent_id', type=int, required=True, help='Element must specify a parent_id')

row_parser = child_parser.copy()
row_parser.add_argument('css', default='', trim=True)


def get_db():
    return db.DB('beacons.sqlite')


def abort_if_item_doesnt_exist(item):
    if item is None:
       abort(404, message="Could not find this resource")


# def item_must_exist(table):
#     def wrapper(func):
#         def function_wrapper(*args, **kwargs):
#             print('----- Decorator <item_must_exist>')
#             print("table: %s" % table)
#             if len(args) > 0:
#                 print("args: %s" % args)
#             print("kwargs: %s" % kwargs)
#             print('func: %s' % func)
#             # print(inspect.getfullargspec(func))
#             # if len(args) > 0:
#             # args[1] kwargs.keys()
#             return func(*args, **kwargs)
#         return function_wrapper
#     return wrapper


class Bookmarks(Resource):

    parser = child_parser.copy()
    parser.add_argument('url', default='', trim=True)
    parser.add_argument('icon', default='', trim=True)


    def get(self, id = None):
        if id is None:
            return get_db().select('bookmark', orderBy='id')
        item = get_db().select('bookmark', unique=True, id=id)
        abort_if_item_doesnt_exist(item)
        return item


    def post(self):
        db = get_db()
        args = Bookmarks.parser.parse_args()
        id = db.insert_object('bookmark', args)
        return db.select('bookmark', unique=True, id=id), 201


    # def delete(self, id):
    #     db = get_db()
    #     item = db.select('bookmark', unique=True, id=id)
    #     abort_if_item_doesnt_exist(item)
    #     db.remove_item('bookmark', id=id)
    #     return '', 204


    # def put(self, id):
    #     item = db.select('bookmark', unique=True, id=id)
    #     abort_if_item_doesnt_exist(item)

    #     args = Bookmarks.parser.parse_args()
    #     db.update_item('bookmark', id=id, *args)

    #     updated_item = db.select('bookmark', unique=True, id=id)
    #     return updated_item, 201


    # def patch(self, id):
    #     item = db.select('bookmark', unique=True, id=id)
    #     abort_if_item_doesnt_exist(item)

    #     args = Bookmarks.parser.parse_args()
    #     db.update_item('bookmark', id=id, *args)

    #     updated_item = db.select('bookmark', unique=True, id=id)
    #     return updated_item, 201


api.add_resource(Bookmarks, '/bookmarks')
api.add_resource(Bookmarks, '/bookmarks/<int:id>', endpoint='id')


if __name__ == '__main__':
    app.run(debug=True, port=5001)

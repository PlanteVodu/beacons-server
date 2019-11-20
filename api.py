import sys
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_restful import reqparse, abort, Api, Resource
import colorama
from colorama import Fore, Back, Style

from beacons_server import db
from resources.bookmark import Bookmark

colorama.init(autoreset=True)

app = Flask(
    __name__,
    static_folder = '',
    static_url_path = '',
    template_folder = ''
)
api = Api(app)

CORS(app, resources={r'/*': {'origins': '*'}})

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


api.add_resource(Bookmark, '/bookmarks')
api.add_resource(Bookmark, '/bookmarks/<int:id>', endpoint='id')


if __name__ == '__main__':
    app.run(debug=True, port=5001)

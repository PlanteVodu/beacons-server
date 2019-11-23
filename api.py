import sys
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_restful import reqparse, abort, Api, Resource
import colorama
from colorama import Fore, Back, Style

from beacons_server import db
from resources.bookmark import Bookmark
from resources.box import Box
from resources.column import Column
from resources.row import Row
from resources.slide import Slide
from resources.beacons import Beacons
from beacons_server import utils

colorama.init(autoreset=True)

app = Flask(
    __name__,
    static_folder = 'dist',
    static_url_path = '',
    template_folder = 'dist'
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


@app.route('/')
def index():
    return render_template('index.html')


api.add_resource(Beacons, '/beacons', endpoint='beacons')

api.add_resource(Bookmark, '/bookmarks', endpoint='bookmarks')
api.add_resource(Bookmark, '/bookmarks/<int:id>', endpoint='bookmark')

api.add_resource(Box, '/boxes', endpoint='box')
api.add_resource(Box, '/boxes/<int:id>', endpoint='boxes')

api.add_resource(Column, '/columns', endpoint='columns')
api.add_resource(Column, '/columns/<int:id>', endpoint='column')

api.add_resource(Row, '/rows', endpoint='rows')
api.add_resource(Row, '/rows/<int:id>', endpoint='row')

api.add_resource(Slide, '/slides', endpoint='slides')
api.add_resource(Slide, '/slides/<int:id>', endpoint='slide')


if __name__ == '__main__':
    app.run(debug=True, port=5001)

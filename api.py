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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/lastbookmarkslocations')
def last_bookmarks_locations():
    db = utils.get_db()

    last_bookmarks = db.select_sql('SELECT MAX(id), parent_id FROM bookmark GROUP BY parent_id ORDER BY id DESC LIMIT 5')
    boxes = [db.select('box', unique=True, id=bm['parent_id']) for bm in last_bookmarks]

    return jsonify(boxes)


@app.route('/beacons/lastmodification')
def db_last_modification():
    return jsonify(utils.get_db_last_modification())


api.add_resource(Beacons, '/beacons', endpoint='beacons')

api.add_resource(Bookmark, '/bookmarks', endpoint='bookmarks')
api.add_resource(Bookmark, '/bookmarks/<int:id>', endpoint='bookmark')

api.add_resource(Box, '/boxes', endpoint='boxes')
api.add_resource(Box, '/boxes/<int:id>', endpoint='box')

api.add_resource(Column, '/columns', endpoint='columns')
api.add_resource(Column, '/columns/<int:id>', endpoint='column')

api.add_resource(Row, '/rows', endpoint='rows')
api.add_resource(Row, '/rows/<int:id>', endpoint='row')

api.add_resource(Slide, '/slides', endpoint='slides')
api.add_resource(Slide, '/slides/<int:id>', endpoint='slide')


if __name__ == '__main__':
    app.run(debug=True, port=5001)

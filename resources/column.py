from flask_restful import reqparse, abort, Resource
from beacons_server import utils

class Column(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('parent_id', type=int)
    parser.add_argument('position', type=int)
    parser.add_argument('name', trim=True)

    full_parser = parser.copy()
    full_parser.replace_argument('parent_id', type=int, required=True, help='Element must specify a parent_id')
    full_parser.replace_argument('position', type=int, help='Element must specify a position')
    full_parser.replace_argument('name', default='', trim=True)


    def abort_if_item_doesnt_exist(self, item):
        if item is None:
            abort(404, message="Could not find the specified column")


    def get(self, id = None):
        if id is None:
            return utils.get_db().select('column', orderBy='id')
        item = utils.get_db().select('column', unique=True, id=id)
        self.abort_if_item_doesnt_exist(item)
        return item


    def post(self):
        db = utils.get_db()
        args = Column.full_parser.parse_args()
        id = db.insert_object('column', args)
        return db.select('column', unique=True, id=id), 201


    def delete(self, id):
        db = utils.get_db()
        item = db.select('column', unique=True, id=id)
        self.abort_if_item_doesnt_exist(item)
        db.remove_item('column', id)
        return '', 204


    def put(self, id):
        db = utils.get_db()
        item = db.select('column', unique=True, id=id)
        args = Column.full_parser.parse_args()
        db.update_item('column', id=id, args=args)
        updated_item = db.select('column', unique=True, id=id)
        return updated_item, 200


    def patch(self, id):
        db = utils.get_db()
        item = db.select('column', unique=True, id=id)
        self.abort_if_item_doesnt_exist(item)

        args = Column.patch_parser.parse_args()
        db.update_item('column', id=id, args=args)

        updated_item = db.select('column', unique=True, id=id)
        return updated_item, 201

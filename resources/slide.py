from flask_restful import reqparse, abort, Resource
from beacons_server import utils

class Slide(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name', trim=True)
    parser.add_argument('position', type=int)

    full_parser = parser.copy()
    full_parser.replace_argument('position', type=int, help='Element must specify a position')
    full_parser.replace_argument('name', default='', trim=True)


    def abort_if_item_doesnt_exist(self, item):
        if item is None:
            abort(404, message="Could not find the specified slide")


    def get(self, id = None):
        if id is None:
            return utils.get_db().select('slide', orderBy='id')
        item = utils.get_db().select('slide', unique=True, id=id)
        self.abort_if_item_doesnt_exist(item)
        return item


    def post(self):
        db = utils.get_db()
        args = Slide.full_parser.parse_args()
        id = db.insert_object('slide', args)
        return db.select('slide', unique=True, id=id), 201


    def delete(self, id):
        db = utils.get_db()
        item = db.select('slide', unique=True, id=id)
        self.abort_if_item_doesnt_exist(item)
        db.remove_item('slide', id)
        return '', 204


    def put(self, id):
        db = utils.get_db()
        item = db.select('slide', unique=True, id=id)
        args = Slide.full_parser.parse_args()
        db.update_item('slide', id=id, args=args)
        updated_item = db.select('slide', unique=True, id=id)
        return updated_item, 200


    def patch(self, id):
        db = utils.get_db()
        item = db.select('slide', unique=True, id=id)
        self.abort_if_item_doesnt_exist(item)

        args = Slide.parser.parse_args()
        db.update_item('slide', id=id, args=args)

        updated_item = db.select('slide', unique=True, id=id)
        return updated_item, 201

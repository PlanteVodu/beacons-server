from flask_restful import reqparse, abort, Resource
from beacons_server import utils

class BasicResource(Resource):

    def __init__(self):
        self.table = self.__class__.__name__.lower()
        self.set_general_parser()
        self.set_get_parser()
        self.set_full_parser()


    def set_general_parser(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('position', type=int)
        self.parser.add_argument('name', trim=True)


    def set_get_parser(self):
        self.get_parser = self.parser.copy()
        self.get_parser.add_argument('_group_by', trim=True)
        self.get_parser.add_argument('_order_by', trim=True)
        self.get_parser.add_argument('_asc', trim=bool)
        self.get_parser.add_argument('_desc', trim=bool)
        self.get_parser.add_argument('_limit', trim=True)

    def set_full_parser(self):
        self.full_parser = self.parser.copy()
        self.full_parser.replace_argument('name', default='', trim=True)


    def abort_if_item_doesnt_exist(self, item):
        if item is None:
            abort(404, message="Could not find the specified item")


    def get(self, id = None):
        args = self.get_parser.parse_args()

        if id is None:
            return utils.get_db().select(self.table, orderBy='id', args=args)

        item = utils.get_db().select(self.table, unique=True, args=args, id=id)
        self.abort_if_item_doesnt_exist(item)

        return item


    def post(self):
        db = utils.get_db()

        args = self.full_parser.parse_args()
        id = db.insert_object(self.table, args)

        item = db.select(self.table, unique=True, id=id)
        return item, 201


    def delete(self, id):
        db = utils.get_db()

        item = db.select(self.table, unique=True, id=id)
        self.abort_if_item_doesnt_exist(item)

        db.remove_item(self.table, id)

        return '', 204


    def patch(self, id):
        db = utils.get_db()

        item = db.select(self.table, unique=True, id=id)
        self.abort_if_item_doesnt_exist(item)

        args = self.parser.parse_args()
        db.update_item(self.table, id=id, args=args)

        updated_item = db.select(self.table, unique=True, id=id)
        return updated_item, 201

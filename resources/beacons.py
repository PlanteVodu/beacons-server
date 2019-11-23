from flask_restful import reqparse, abort, Resource
from beacons_server import utils

class Beacons(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('until', default='', trim=True)
    parser.add_argument('transform', type=bool, default=False)

    def get(self):
        args = Beacons.parser.parse_args()

        db = utils.get_db()
        db.SILENT = True
        beacons = db.get_items_with_descendants('slide', until=args['until'])
        db.SILENT = False

        if not args['transform'] or args['transform'] == 'false':
            return beacons

        grid_items = []
        nb_rows = 0

        for slide in beacons:
            nb_rows = max(nb_rows, len(slide['content']))
            for index, row in enumerate(slide['content']):
              row['position'] = index + 1
              row['slideId'] = slide['id']
              row['slidePosition'] = slide['position'] + 1
              # row['slideCss'] = slide['css']
              grid_items.append(row)

        return grid_items

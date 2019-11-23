from resources.child_resource import ChildResource

class Bookmark(ChildResource):

    def __init__(self):
        ChildResource.__init__(self)

        self.parser.add_argument('url', trim=True)
        self.parser.add_argument('icon', trim=True)

        self.full_parser.add_argument('url', default='', trim=True)
        self.full_parser.add_argument('icon', default='', trim=True)

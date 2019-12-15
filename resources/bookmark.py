from resources.child_resource import ChildResource

class Bookmark(ChildResource):

    def set_general_parser(self):
        ChildResource.set_general_parser(self)
        self.parser.add_argument('url', trim=True)
        self.parser.add_argument('icon', trim=True)


    def set_full_parser(self):
        ChildResource.set_full_parser(self)
        self.full_parser.add_argument('url', default='', trim=True)
        self.full_parser.add_argument('icon', default='', trim=True)

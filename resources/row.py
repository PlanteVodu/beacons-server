from resources.child_resource import ChildResource

class Row(ChildResource):

    def set_general_parser(self):
        ChildResource.set_general_parser(self)
        self.parser.add_argument('css', trim=True)

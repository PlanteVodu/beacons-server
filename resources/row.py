from resources.child_resource import ChildResource

class Row(ChildResource):

    def __init__(self):
        ChildResource.__init__(self)

        self.parser.add_argument('css', trim=True)

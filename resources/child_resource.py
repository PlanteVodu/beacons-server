from resources.basic_resource import BasicResource

class ChildResource(BasicResource):

    def __init__(self):
        BasicResource.__init__(self)
        self.parser.add_argument('parent_id', type=int)
        self.full_parser.add_argument('parent_id', type=int, required=True)

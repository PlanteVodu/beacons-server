from resources.basic_resource import BasicResource

class ChildResource(BasicResource):

    def set_general_parser(self):
        BasicResource.set_general_parser(self)
        self.parser.add_argument('parent_id', type=int)


    def set_full_parser(self):
        BasicResource.set_full_parser(self)
        self.full_parser.add_argument('parent_id', type=int, required=True)

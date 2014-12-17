class Node(object):
    """some item in the traversal tree"""
    __name__ = ''
    __parent__ = None

    def __init__(self, request):
        self.request = request
    def __getitem__(self, key):
        if key == 'site':
            child =  SiteDispatcher(self.request)
        elif key == 'camera':
            child = CameraDispatcher(self.request)
        else:
            raise KeyError(key)
        child.__name__ = key
        child.__parent__ = self
        return child
    def __str__(self):
        return "{}->{}({})".format(self.__parent__, self.__class__.__name__, self.__name__)

class Root(Node):
    pass
class DataNode(Node):
    def __init__(self, *args, **kwargs):
        self.data = None
        super(DataNode,self).__init__(*args, **kwargs)


class Dispatcher(Node):
    _type = None
    @classmethod
    def set_type(cls, type_):
        cls._type = type_

    def __getitem__(self, key):
        # Look up info in the database the database here:

        # Use either info from
        # self.request
        # self.__parent__

        data = {'key': key}
        art = self._type(self.request)
        art.data = data
        art.__name__ = key
        art.__parent__ = self
        return art



# This is just semantics... (for now)
class Site(DataNode):
    pass
class SiteDispatcher(Dispatcher):
    pass
SiteDispatcher.set_type(Site)

class Camera(DataNode):
    pass
class CameraDispatcher(Dispatcher):
    pass
CameraDispatcher.set_type(Camera)


def root_factory(request):
    return Root(request)

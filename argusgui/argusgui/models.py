from pyramid.security import Allow

class RootFactory(object):
    __acl__ = [ (Allow, 'group:viewers', 'view'),
                (Allow, 'group:editors', 'edit') ]
    def __init__(self, request):
        pass
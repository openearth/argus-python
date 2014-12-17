from pyramid.config import Configurator
from basic_authentication import BasicAuthenticationPolicy, mycheck
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.renderers import JSON, JSONP
from pyramid.httpexceptions import HTTPNotFound

def not_found(request):
    return HTTPNotFound()

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory='argusgui.models.RootFactory',
                          settings=settings,
                          authentication_policy=BasicAuthenticationPolicy(mycheck), 
                          authorization_policy=ACLAuthorizationPolicy())

    # renderers
    config.add_renderer('jsonp', JSONP(param_name='callback'))
    config.include('pyramid_chameleon')

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('image', 'datasets', cache_max_age=3600)
    config.add_route('gui_home', '/')
    config.add_route('gui_classification', '/classification/')
    config.add_route('gui_compare', '/classification/compare/')
    config.add_route('gui_test', '/test/')
    config.add_route('queue', '/classification/queue/')
    config.add_route('train', '/classification/train/{dataset}/')
    config.add_route('datasets', '/datasets/')
    config.add_route('compare', '/datasets/compare/')
    config.add_route('dataset', '/datasets/{dataset}/')
    config.add_route('image', '/datasets/{dataset}/{image}/')
    config.add_notfound_view(not_found, append_slash=True)
    config.scan()
    return config.make_wsgi_app()

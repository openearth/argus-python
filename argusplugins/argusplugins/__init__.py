from pyramid.config import Configurator
from pyramid.renderers import JSON, JSONP

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')

    # renderers
    config.add_renderer('jsonp', JSONP(param_name='callback'))

    # routes
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('list', '/plugins')
    config.add_route('options', '/plugins/{plugin}')
    config.add_route('run', '/plugins/*plugins')
    config.scan()
    return config.make_wsgi_app()

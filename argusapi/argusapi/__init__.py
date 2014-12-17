import decimal
import functools
import json

from pyramid.config import Configurator
from pyramid.renderers import JSON, JSONP
from sqlalchemy import engine_from_config

from .resources import (
    root_factory
)
from .models import (
    DBSession,
    Base,
    metadata,
    update_metadata,
    ExtendedEncoder
)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # database stuff
#    engine = engine_from_config(settings, 'sqlalchemy.')
#    DBSession.configure(bind=engine)
#    Base.metadata.bind = engine
#    metadata.bind = engine
    # update the metdata table
#    metadata.reflect()
    # update with custom types
#    update_metadata(metadata)

    config = Configurator(settings=settings)

    # renderers
    config.add_renderer('jsonp', JSONP(param_name='callback'))
    config.include('pyramid_chameleon')

    # static content
    config.add_static_view('static', 'static', cache_max_age=3600)

    # url dispatch configuration
    config.add_route('home', '/')
    config.add_route('table', '/table/{table}*filter')
    config.add_route('tables', '/table')
    config.add_route('field', '/field/{datatype}')
    config.add_route('image', '/image')

    # url traversal
    config.add_route('traverse', '/traverse/*traverse', factory=root_factory)
    config.add_view('argusapi.views.overview', route_name='traverse',
                    name='overview')

    config.scan()
    return config.make_wsgi_app()

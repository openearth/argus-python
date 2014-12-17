from pyramid.view import view_config
from pyramid.response import Response

import json
import plugin

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'argusplugins'}

@view_config(route_name='list', renderer='jsonp')
def list_plugins(request):
    """get an overview of all plugins and return as jsonp"""
    plugins = plugin.get_plugins()
    return plugins

@view_config(route_name='options', renderer='jsonp')
def list_plugin_options(request):
    """get an overview of all options for a specific plugin and return as jsonp"""
    options = {}
    options.update(plugin.get_plugin_options(request.matchdict['plugin']))
    options.update(plugin.get_plugin_vizoptions(request.matchdict['plugin']))
    return options

@view_config(route_name='run', renderer='jsonp')
def run_plugin(request):
    """run plugin and return image"""
    img = plugin.run_plugins(request.matchdict['plugins'][:-1],
                             request.matchdict['plugins'][-1],
                             request,
                             plot=True)
    
    response = Response(body=img, content_type='image/jpeg')

    return response

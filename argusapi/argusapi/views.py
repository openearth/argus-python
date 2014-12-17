import json

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.traversal import find_resource, find_interface

from .resources import (
    Site,
    Camera
)

import models
import fielddata
import imgdata


def parse_filter(request):
    """
    Get the parameter filter from the request and split up into key value pairs.
    """
    # if odd
    filter = list(request.matchdict.get('filter', []))
    assert len(filter) % 2  == 0
    keys = filter[0::2]
    values = filter[1::2]
    query = dict(zip(keys, values))
    query.update(request.params)
    for q in ['callback', '_']:
        if q in query:
            query.pop(q)
    return query


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    """home page"""
    return {'project': 'argusapi'}


@view_config(route_name='table', renderer='jsonp')
def table(request):
    """get information from a mysql table and return as jsonp"""
    models.update_metadata(models.metadata)
    table_name = request.matchdict['table']
    query = parse_filter(request)
    rs = models.get_table(table_name, query=query)
    # dump to json
    # don't use the default encoder because it doesn't support
    # iterators or sqlalchemy proxy
    encoder = models.ExtendedEncoder()
    return json.loads(encoder.encode(rs))

@view_config(route_name='tables', renderer='jsonp')
def tables(request):
    """get an overview of all tables and return as jsonp"""
    models.update_metadata(models.metadata)
    rs = models.get_tables()
    encoder = models.ExtendedEncoder()
    return json.loads(encoder.encode(rs))

@view_config(route_name='field', renderer='jsonp')
def field(request):
    """get field data for a certain location/time"""
    datatype = request.matchdict['datatype']
    if hasattr(fielddata, datatype):
        fcn = getattr(fielddata, datatype)
        data = fcn(
            request.params.get('lat', 0),
            request.params.get('lon', 0),
            request.params.get('datetime', None),
            request.params.get('duration', 0)    )
        return data
    else:
        raise ValueError('Unknown datatype [%s]' % datatype)

@view_config(route_name='image', renderer='jsonp')
def image(request):
    url = request.params.get('url','')
    rs = imgdata.get_imgdata(url)
    encoder = models.ExtendedEncoder()
    return json.loads(encoder.encode(rs))

def overview(request):
    site_resource = find_resource(request.context, '/site/b')
    site_interface = find_interface(request.context, Site)
    camera = find_interface(request.context, Camera)
    txt = "{:s}\n{:s}\n{:s}\n{:s}".format(site_resource, site_interface, camera, request.context)
    response = Response(txt)
    response.content_type = 'text/plain'
    return response

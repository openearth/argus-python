import socket
import urllib2
import json

tables = ['images', 'imagesets']

def exists(table_name):

    return table_name in tables
    
def get_table(table_name, **params):

    if table_name == 'images':
        return _vt_images(params)
    if table_name == 'imagesets':
        return _vt_imagesets(params)
    else:
        raise ValueError('Unknown virtual table [%s]' % table_name)

def _vt_images(params):

    host = 'argus-public.deltares.nl'
    
    if _host_is_up(host,80):
            
        url        = 'http://%s/catalog/?output=json' % host
        json_query = url + '&' + '&'.join(['%s=%s' % (k,v) for k,v in params.iteritems()])
        json_data  = urllib2.urlopen(json_query).read()

        if len(json_data) > 0:
            data   = json.loads(json_data)
            
            if type(data) is dict and data.has_key('data'):
                data = [dict(p, path=data['urlPrefix']+p['path']+data['urlSuffix']) for p in data['data']]
            else:
                data = []
        else:
            data   = []

        print json_query
        
    else:
        raise ValueError('Host not reachable [%s]' % host)
        
    return data
        
def _vt_imagesets(params):
    
    data = _vt_images(params)
    data = sorted(list(set([int(d['epoch']/600)*600 for d in data])))
        
    return data
    
def _host_is_up(host, port=80):
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        is_up = True
    except socket.error:
        is_up = False

    sock.close()
    
    return is_up

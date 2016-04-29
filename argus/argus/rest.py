import urllib2
import json
import re
import cStringIO
import matplotlib.pyplot as plt
import numpy as np

import filename

#HOST = r'http://argus-public.deltares.nl/'
HOST = r'http://136.231.49.12/'

def get_rectification_data(station):

    rp = {}

    # read station
    station = __get_data('station', shortName=station)[0]

    # read camera
    cameras = __get_data('camera', stationId=station['id'])

    for cam in cameras:

        # read ip
        #ip = __get_data('IP', id=camera['IPID'])

        cid = cam['cameraNumber']
    
        rp[cid] = {}
        rp[cid]['K'] = np.asarray(cam['K']).T
        rp[cid]['D_U0'] = cam['D_U0']
        rp[cid]['D_V0'] = cam['D_V0']
        rp[cid]['D1'] = cam['D1']
        rp[cid]['D2'] = cam['D2']
        rp[cid]['Drad'] = np.asarray(cam['Drad']).flatten()
        rp[cid]['Dtan'] = np.asarray(cam['Dtan']).flatten()
    
        rp[cid]['UV'] = []
        rp[cid]['XYZ'] = []
  
        # read geometry
        geometry = __get_data('geometry', cameraID=cam['id'])[0]
    
        # read used gcp's
        usedgcps = __get_data('usedGCP', geometrySequence=geometry['seq'])
    
        for usedgcp in usedgcps:
        
            # read used gcp's
            gcp = __get_data('gcp', id=usedgcp['gcpID'])[0]
    
            rp[cid]['UV'].append((usedgcp['U'], usedgcp['V']))
            rp[cid]['XYZ'].append((gcp['y'], gcp['x'], gcp['z']))

    return rp

def get_rotation_data(station):

    rp = {}

    # read station
    station = __get_data('station', shortName=station)[0]

    # read site
    site = __get_data('site', id=station['siteID'])[0]

    rp['translation'] = np.asarray(site['coordinateOrigin']).flatten()
    rp['rotation'] = site['coordinateRotation'] - 90

    return rp

def get_image_list(station, **kwargs):
    query = '&'.join(['='.join((k,w)) for k,w in kwargs.iteritems()])
    fp = urllib2.urlopen('%s/catalog?site=%s&%s&output=json' % (HOST, station, query))
    data = json.load(fp)
    fp.close()

    return [''.join([data['urlPrefix'], x['path'], data['urlSuffix']]) for x in data['data']]

def get_image(fname):
    if re.match('^\w+:\/\/', fname):
        return get_image_url(fname)
    else:
        return get_image_url(filename.filename2url(fname))

def get_image_url(url, slice=0):
  'Get image date from URL'
  
  f = cStringIO.StringIO(read_url_contents(url))
  img = plt.imread(f, format='jpg')
  
  if slice > 0:
    img = img[::slice,::slice,:]
    
  img = img[:,:,:3]/255.0 # FIXME: ignore alpha
  
  return img

def read_url_contents(url):
    'Read entire contents of URL'
    
    regex = re.compile('[Zz]andmotor?')
    if regex.search(url):
        url = __get_auth_zm(url)
    
    try:
        return urllib2.urlopen(url).read()
    except:
        return None
        
def __get_auth_zm(url):
    
    req = urllib2.Request(url)
    unpw = 'emFtbzpkZWxmbGFuZHNla3VzdA=='
    authheader =  "Basic %s" % unpw
    req.add_header("Authorization", authheader)
    
    return req

def __get_data(table, **kwargs):
    query = '&'.join(['='.join((k,str(v))) for k,v in kwargs.iteritems()])
    url = '%s/db/table/%s?%s' % (HOST, table, query)
    fp = urllib2.urlopen(url)
    data = json.load(fp)
    fp.close()
    
    return data

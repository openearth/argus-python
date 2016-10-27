import urllib2
import json
import re
import cStringIO
import matplotlib.pyplot as plt
import numpy as np
import logging

import filename

logger = logging.getLogger(__name__)

def get_rectification_data(host, station):
    '''Get rectification data'''

    rp = {}

    # read station
    station = _get_data(host, 'station', shortName=station)
    logger.debug(station)
    
    if len(station) > 0:
        station = station[0]

        # read camera
        cameras = _get_data(host, 'camera', stationId=station['id'])
        logger.debug(cameras)

        for cam in cameras:

            # read ip
            #ip = _get_data('IP', id=camera['IPID'])

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
            geometry = _get_data(host, 'geometry', cameraID=cam['id'])
            logger.debug(geometry)

            if len(geometry) > 0:
                geometry = geometry[0]
    
                # read used gcp's
                usedgcps = _get_data(host, 'usedGCP', geometrySequence=geometry['seq'])
                logger.debug(usedgcps)
    
                for usedgcp in usedgcps:
        
                    # read used gcp's
                    gcp = _get_data(host, 'gcp', id=usedgcp['gcpID'])
                    logger.debug(gcp)

                    if len(gcp) > 0:
                        gcp = gcp[0]
                        rp[cid]['UV'].append((usedgcp['U'], usedgcp['V']))
                        rp[cid]['XYZ'].append((gcp['y'], gcp['x'], gcp['z']))

    return rp


def get_rotation_data(host, station):
    '''Get rotation data'''

    rp = {}

    # read station
    station = _get_data(host, 'station', shortName=station)
    logger.debug(station)

    if len(station) > 0:
        station = station[0]

        # read site
        site = _get_data(host, 'site', id=station['siteID'])
        logger.debug(site)

        if len(site) > 0:
            site = site[0]

            rp['translation'] = np.asarray(site['coordinateOrigin']).flatten()
            rp['rotation'] = site['coordinateRotation'] - 90

    return rp


def get_image_list(host, station, **kwargs):
    '''Get list of url's of available images

    Parameters
    ----------
    host : str
        Host name
    station : str
        Name of Argus station (e.g., aberdees, egmond, sete,
        zandmotor)
    startEpoch : int
        Specifies the earliest time for which results are returned. If
        omitted or zero, only the single most recent image or product
        is returned (useful only in combination with other clauses). A
        negative value means "now" minus the specified number of
        seconds.
    endEpoch : int
        Specifies the latest time for which results are returned. If
        omitted or non-positive, the current time is used.
    camera : int
        Limit results to the specified camera. This only applies to
        raw image data (snap, timex, stack, etc.).
    type : str
        The type of image or data product to return. If unspecified,
        everything is returned.  The following types are recognized:
        Basic images: snap, timex, var, min, max Pixel time series: stack
        Merges: plan, pan
    timeOfDay : int
        Limit results to the specified time of day, expressed as
        minutes after midnight, plus or minus 2.5 minutes, in the
        local time zone. Argus images are typically collected on the
        whole and half hour.  Stacks can start any time, but usually
        last 17 minutes.
    limit : int
        Limit the number of URLs to be returned. Default is 1000,
        which is also the maximum for anonymous users. A negative
        value limits output to most recent results.
    user : str
        Identifies the user for non-public data.
    auth : str
        Autorization code (requires the use of the HTTPS protocol).

    Returns
    -------
    list of str
        List with full URL's

    '''
    
    query = '&'.join(['='.join((k,str(w))) for k,w in kwargs.iteritems()])
    fp = urllib2.urlopen('%s/catalog?site=%s&%s&output=json' % (host, station, query))
    data = json.load(fp)
    fp.close()

    return [''.join([data['urlPrefix'], x['path'], data['urlSuffix']])
            for x in data['data']]


def _get_data(host, table, **kwargs):
    '''Raw data read from REST API'''
    
    query = '&'.join(['='.join((k,str(v))) for k,v in kwargs.iteritems()])
    url = '%s/db/table/%s?%s' % (host, table, query)
    fp = urllib2.urlopen(url)
    data = json.load(fp)
    fp.close()
    
    return data


def get_image(url, slice=0):
  '''Get image data from URL'''
  
  f = cStringIO.StringIO(read_url_contents(url))
  img = plt.imread(f, format='jpg')
  
  if slice > 0:
    img = img[::slice,::slice,:]
    
  img = img[:,:,:3]/255.0 # FIXME: ignore alpha
  
  return img


def read_url_contents(url):
    '''Read entire contents of URL'''
    
    try:
        return urllib2.urlopen(url).read()
    except:
        return None

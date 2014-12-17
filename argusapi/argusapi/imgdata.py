import pyproj
import pytz

from .filename import filename2fileparts, filename2dayfile, filename2datetime
import models
import fielddata

def get_imgdata(imgfile):

    imgdata = {
        'file':     {},
        'site':     {},
        'station':  {},
        'camera':   {},
        'datetime': {},
        'field':    {}
    };

    # parse filename
    fileparts = filename2fileparts(imgfile)

    if not fileparts is None:

        imgdata['file'] = fileparts

        # add date/time strings
        tz = pytz.timezone('Europe/Amsterdam')

        dtutc   = filename2datetime(imgfile).replace(tzinfo=pytz.utc)
        dttz    = dtutc.astimezone(tz)

        imgdata['datetime']['timezone'] = dttz.strftime('%Z')
        imgdata['datetime']['datetime'] = dttz.strftime('%Y-%m-%d %H:%M')
        imgdata['datetime']['date']     = dttz.strftime('%Y-%m-%d')
        imgdata['datetime']['time']     = dttz.strftime('%H:%M')

        # add site and station data
        stations = models.get_table('station', {'shortname':imgdata['file']['station']})
        imgdata['station'] = stations[0] if stations else {}
        sites = models.get_table('site',
                                 {'id':imgdata['station'].get('siteID','')}
        )
        imgdata['site']    = sites[0] if sites else {}
        cameras = models.get_table('camera',
                                   {'stationID':imgdata['station'].get('id',''),
                                    'cameraNumber':int(imgdata['file']['camera'])}
        )
        imgdata['camera']  = cameras[0] if cameras else {}

        # add location
        wgs84 = pyproj.Proj('+init=EPSG:4326')
        org   = pyproj.Proj('+init=EPSG:%d' % imgdata['site'].get('coordinateEPSG', 28992))

        x, y, z = imgdata['site'].get('coordinateOrigin', [[0,0,0]])[0]

        lon, lat = pyproj.transform(org, wgs84, x, y)

        imgdata['site']['lat'] = lat
        imgdata['site']['lon'] = lon

        # add field data
        imgdata['field']['sun']   = fielddata.sun(lat, lon, dt=dtutc.strftime('%Y-%m-%d %H:%M'))
        imgdata['field']['tide']  = fielddata.tide(lat, lon, dt=dtutc.strftime('%Y-%m-%d %H:%M'))
        imgdata['field']['meteo'] = fielddata.meteo(lat, lon, dt=dtutc.strftime('%Y-%m-%d %H:%M'))

    return imgdata

import ephem
import math
import pytz
import netCDF4
import pyproj
import bisect
from datetime import datetime, timedelta

def sun(lat, lon, dt=None, duration=0):

    fieldnames = ['a_dec', 'a_epoch', 'a_ra', 'alt', 'az', 'circumpolar',
                  'dec', 'earth_distance', 'elong', 'g_dec', 'g_ra', 'hlat',
                  'hlon', 'hlong', 'mag', 'name', 'neverup', 'phase', 'ra',
                  'radius', 'rise_az', 'rise_time', 'size', 'sun_distance',
                  'transit_alt', 'transit_time']

    lat, lon, dt = _purifyInput(lat, lon, dt, duration)

    o             = ephem.Observer()
    o.lat, o.long = str(lat), str(lon)
    o.elevation   = 0

    response      = []
    cdt           = dt[0]

    while cdt<=dt[1]:
        o.date    = pytz.utc.localize(cdt)
        sun       = ephem.Sun(o)

        response.append({fieldname:getattr(sun, fieldname) for fieldname in fieldnames})

        cdt       = cdt + timedelta(0,600)

    response = {f:[r[f] for r in response] for f in fieldnames}

    return response

def tide(lat, lon, dt=None, duration=0):

    lat, lon, dt = _purifyInput(lat, lon, dt, duration)

    # read catalog
    catalog = 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/waterbase/sea_surface_height/catalog.nc'
    ncfile  = _getNetCDFFromCatalog(catalog, lat, lon)
    ncfile  = 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/waterbase/sea_surface_height/id1-SCHEVNGN.nc' # fixme

    # read nc file
    idx     = _getNetCDFIndexFromDatetime(ncfile, dt)

    if None in idx:
        response    = {}
    else:
        nc      = netCDF4.Dataset(ncfile, 'r')
        i0, i1  = idx[:]
        i1      = max(i0+1,i1)

        sea_surface_height = nc.variables['sea_surface_height'][0,i0:i1]
        sea_surface_height = [round(s*100)/100 for s in sea_surface_height]

        response    = {
            'platform_id'   : ''.join(nc.variables['platform_id'][0]),
            'platform_name' : ''.join(nc.variables['platform_name'][0]),
            'lon'           : float(nc.variables['lon'][0]),
            'lat'           : float(nc.variables['lat'][0]),
            'sea_surface_height' : sea_surface_height }
        nc.close()
    return response

def meteo(lat, lon, dt=None, duration=0):

    lat, lon, dt = _purifyInput(lat, lon, dt, duration)

    # read catalog
    catalog = 'http://opendap.deltares.nl/thredds/dodsC/opendap/knmi/uurgeg/old/catalog.nc'
    ncfile  = _getNetCDFFromCatalog(catalog, lat, lon)
    ncfile  = 'http://opendap.deltares.nl/thredds/dodsC/opendap/knmi/uurgeg/uurgeg_330_2011-2020.nc'

    # read nc file
    idx     = _getNetCDFIndexFromDatetime(ncfile, dt)

    if None in idx:
        response    = {}
    else:
        nc      = netCDF4.Dataset(ncfile, 'r')
        i0, i1  = idx[:]
        i1      = max(i0+1,i1)

        params  = ['wind_from_direction_mean', 'wind_speed_vector_mean', 'wind_speed_vector_mean_10min', 'wind_speed_minimum_gust_hour',
                   'air_temperature_mean', 'air_temperature_minimum', 'dew_point_temperature', 'duration_of_sunshine', 'global_radiation',
                   'precipitation_duration', 'precipitation_amount_sum', 'surface_air_pressure', 'visibility_in_air', 'cloud_cover',
                   'relative_humidity', 'weather_code', 'weather_registration_method', 'fog', 'rain', 'snow', 'thunder', 'ice'];

        response    = {
                    'platform_id'   : int(nc.variables['platform_id'][0]),
                    'platform_name' : ''.join(nc.variables['platform_name'][0]),
                    'lon'           : float(nc.variables['lon'][0]),
                    'lat'           : float(nc.variables['lat'][0])}

        for param in params:

            p = nc.variables[param][0,i0:i1]
            p = [round(s*100)/100 for s in p]

            response[param] = p
        nc.close()
    return response

def _getNetCDFFromCatalog(url, lat, lon):

    nc     = netCDF4.Dataset(url, 'r')
    nc_url = nc.variables['urlPath']
    nc_lat = nc.variables['geospatialCoverage_northsouth_start'][:].flatten()
    nc_lon = nc.variables['geospatialCoverage_eastwest_start'][:].flatten()

    dst    = [math.sqrt(x) for x in (nc_lat-lat)**2+(nc_lon-lon)**2]
    idx    = min(range(len(nc_url)), key=lambda i: dst[i])

    ncfile = ''.join(nc_url[idx])

    return ncfile

def _getNetCDFIndexFromDatetime(url, dt, maxdev=1.0/24):

    nc      = netCDF4.Dataset(url, 'r')
    t       = nc.variables['time']
    n       = len(t) - 1
    dtnum   = netCDF4.date2num(dt, units=t.units)

    idx     = [None] * len(dtnum)
    lo      = 0
    for i in range(len(dtnum)):
        idx[i]  = min(n,bisect.bisect_left(t, dtnum[i], lo=lo))
        lo      = idx[i]

        if abs(t[idx[i]]-dtnum[i]) > maxdev:
            idx[i] = None
    nc.close()
    return idx

def _purifyInput(lat, lon, dt, duration=None):

    if dt is None:
        dt = datetime.now()

    if isinstance(lat,unicode):
        lat = str(lat)

    if isinstance(lat,str):
        lat = float(lat)

    if isinstance(lon,unicode):
        lon = str(lon)

    if isinstance(lon,str):
        lon = float(lon)

    if isinstance(dt,unicode):
        dt = str(dt)

    if isinstance(dt,str):
        dt = datetime.strptime(dt,'%Y-%m-%d %H:%M')

    if isinstance(duration,unicode):
        duration = str(duration)

    if isinstance(duration,str):
        duration = float(duration)

    if isinstance(duration,float) or isinstance(duration,int):
        duration = timedelta(duration/2.0)

    if not duration is None:
        dt = [dt - duration, dt + duration]

    return (lat, lon, dt)

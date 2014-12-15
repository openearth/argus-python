import re
import datetime
import pytz

HOST = r'http://argus-data.wldelft.nl/sites'

argusname = re.compile(
    r'(?P<timestamp>\d+)' # timestamp
    r'\.'                 
    r'(?P<weekday>\w+)'   # short day
    r'\.'                 
    r'(?P<month>\w+)'     # short month
    r'\.'                 
    r'(?P<day>\d+)'       # day
    r'_'                  
    r'(?P<hour>\d+)'      # hours
    r'_'                  
    r'(?P<minute>\d+)'    # minutes
    r'_'                  
    r'(?P<second>\d+)'    # seconds
    r'\.'                 
    r'(?P<tz>\w+)'        # time zone
    r'\.'                 
    r'(?P<year>\d+)'      # year
    r'\.'                 
    r'(?P<station>\w+)'   # station
    r'\.'                 
    r'c(?P<camera>[\dx]+)'# camera
    r'\.'                 
    r'(?P<imgtype>\w+)'   # image type
    r'(\.product_(?P<product>\d+))?' # [optional] product
    r'\.'                 
    r'(?P<extension>\w+)' # extension
    )
    
def url2filename(url):

    m = argusname.search(url)
        
    if m == None:
        return None
    else:
        return m.group()

def filename2url(filename, host=HOST):
    m = filename2fileparts(filename)
    d = filename2datetime(filename)
    url = '%s/%s/%s/c%s/%03d_%s.%s/%s' % (host,
                                          m['station'],
                                          m['year'],
                                          m['camera'],
                                          int(d.strftime('%j')),
                                          m['month'],
                                          m['day'],
                                          filename)
    return url

def filename2dayfile(filename):

    m = filename2fileparts(filename)
    
    if m == None:
        return None
    else:
        return '%s.%s.%s.%s.%s' % (m['month'], m['day'], m['year'], m['station'], m['camera'])
        
def filename2fileparts(filename):

    m = argusname.search(filename)
            
    if m == None:
        return None
    else:
        return m.groupdict()
    
def filename2datetime(filename):
    
    m = filename2fileparts(filename)
    
    if m == None:
        return None
    else:
        return fileparts2datetime(**{k:v for k,v in m.iteritems() if k in ['year','month','day','hour','minute','second', 'tz']})
        
def fileparts2datetime(year=None, month=None, day=None, hour=None, minute=None, second=None, tz=None, series=None):

    kwarg  = locals()
    kwargs = kwarg.copy()
    
    dateKeys = ('year', 'month', 'day')
    timeKeys = ('hour', 'minute', 'second')
    
    hasDate = False
    hasTime = False
    
    if year != None or month != None or day != None:
        hasDate = True
        
    if hour != None or minute != None or second != None or series != None:
        hasTime = True

    for k, v in kwarg.iteritems():
        if v == None or (type(v) == str and len(v) == 0):
            if kwargs[k] == None:
                if k in dateKeys:
                    kwargs[k] = 1
                else:
                    kwargs[k] = 0
        else:
            if k == 'month':
                try:
                    kwargs[k] = datetime.datetime.strptime(v, '%b').month
                except:
                    kwargs[k] = datetime.datetime.strptime(v, '%B').month
            elif k == 'day':
                try:
                    kwargs[k] = datetime.datetime.strptime(v, '%a %d').day
                except:
                    kwargs[k] = int(v)
            elif k == 'series':
                try:
                    oDate = datetime.datetime.strptime(v, '%H:%M')
                    kwargs['hour']   = oDate.hour
                    kwargs['minute'] = oDate.minute
                except:
                    pass
            elif k == 'tz':
                pass
            else:
                kwargs[k] = int(v)

    if hasDate and hasTime:
        dt = datetime.datetime(**{k:v for k,v in kwargs.iteritems() if k not in ('series', 'tz')})
        
        # make timezone aware and convert to UTC
        if not tz is None:
            tz = pytz.timezone(tz)
            dt = tz.localize(dt)
            dt = dt.astimezone(pytz.utc)
            
        return dt
    elif hasDate:
        return datetime.date(**{k:v for k,v in kwargs.iteritems() if k in dateKeys})
    elif hasTime:
        return datetime.time(**{k:v for k,v in kwargs.iteritems() if k in timeKeys})
    else:
        return None

def datetime2regex(oDate):

    if type(oDate) is datetime.time:
        regex = oDate.strftime('\d+\.\w+\.\w+\.\d+_%H_%M_%S\.\w+\.\d+\.\w+\.c\d+\.\w+\.jpg')
    elif type(oDate) is datetime.date:
        regex = oDate.strftime('\d+\.%a\.%b\.%d_\d+_\d+_\d+\.\w+\.%Y\.\w+\.c\d+\.\w+\.jpg')
    elif type(oDate) is datetime.datetime:
        regex = oDate.strftime('\d+\.%a\.%b\.%d_%H_%M_%S\.\w+\.%Y\.\w+\.c\d+\.\w+\.jpg')
    
    return regex

def overview_year_url(station, year, host=HOST):
    
    return '%s/%s/%s/index.html' % (host, station, year)
    
def overview_day_url(station, oDate, type='snap', host=HOST):
    
    if re.match('c\d+$', type):
        return oDate.strftime('%s/%s/%%Y/%s/%%j_%%b.%%d/index.html' % (host, station, type))
    else:
        return oDate.strftime('%s/%s/%%Y/cx/%%j_%%b.%%d/%s.html' % (host, station, type))
        
def image_url(station, year, url, host=HOST):

    return '/'.join((host, station, year, url))

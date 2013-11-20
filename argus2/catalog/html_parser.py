import re
import urllib2
import datetime
import time
import numpy as np
import random

from argus2 import filesys

###############################################################################

def get_station_years(station):
    'Parse all image data from a single station'

    years = []
    year  = datetime.datetime.now().year

    # start loop years
    while True:
    
        print 'Parsing year %d...' % year

        contents = filesys.url.read_url_contents(filesys.url.overview_year_url(station, year))

        if contents != None:
            years.append(year)
        else:
            break

        year = year - 1

    years.reverse()

    return years

###############################################################################

def get_station_months(station, year):

    series = parse_station_year(station, year)
    
    return sorted(series.keys(), key=lambda m: time.strptime(m, '%B'))

def get_station_days(station, year, month):

    series = parse_station_year(station, year)
    
    return [d.strftime('%a %d') for d in sorted(series[month])]
    
def get_station_series(station, year, month, day):

    series = parse_station_day(station, year, month, day)
    
    return [d[0].strftime('%H:%M') for d in series]
    
def get_station_images(station, year=None, month=None, day=None, series=None):

    imgtype='snap';
    
    oDate   = filesys.filename.fileparts2datetime(year=year, month=month, day=day, series=series)

    url     = filesys.url.overview_day_url(station, oDate, type=imgtype)
    urls    = filesys.url.extract_image_urls(url, oDate)
    
    return [filesys.url.image_url(station, year, url) for url in urls]
    
def get_random_image(stations):

    image = []
    
    station = pick_random(stations)
    year    = str(pick_random(get_station_years(station)))
        
    while len(image) == 0:
        month   = pick_random(get_station_months(station, year))
        day     = pick_random(get_station_days(station, year, month))
        series  = pick_random(get_station_series(station, year, month, day))
        image   = pick_random(get_station_images(station, year, month, day, series))
    
    return [image]
    
def get_station_cameras(station,year):
    
    url = filesys.url.overview_year_url(station,year)
    content = filesys.url.read_url_contents(url)
    
    regexp = re.compile('Cam\s+\d')
    cameras = regexp.findall(content)
    
    for i in range(len(cameras)):
        cameras[i] = re.sub('\D','',cameras[i])
    
    cameras = list(np.unique(cameras))
    
    return cameras
    
def parse_station_year(station, year):
    'Parse a HTML year overview and return sorted list of timestamps'
    
    series = {}

    contents = filesys.url.read_url_contents(filesys.url.overview_year_url(station, year))

    # compile regular expressions
    regex1 = re.compile('<tr><td><p>(\d{3})_(\w{3})\.(\d{2})</p></td>\s*((<td.*?>.*?</td>\s*)+)</tr>');

    if contents != None:
        m = regex1.findall(contents)

        # loop over days
        for i in range(len(m)):

            #print 'Parsing day %d of year %s...' % (int(m[i][0]), year)

            yearDay     = int(m[i][0])
            oDate       = datetime.date(int(year), 1, 1) + datetime.timedelta(yearDay - 1)
            monthName   = oDate.strftime('%B')
            
            if not series.has_key(monthName):
                series[monthName] = []

            series[monthName].append(oDate)

    return series
    
def parse_station_day(station, year, month, day, imgtype='snap'):

    series = []
    
    oDate   = filesys.filename.fileparts2datetime(year, month, day)
    url     = filesys.url.overview_day_url(station, oDate, type=imgtype)
    urls    = filesys.url.extract_image_urls(url)

    if len(urls) > 0:

        oDate = sorted([filesys.filename.filename2datetime(url) for url in urls])

        l = 0
        for i in range(len(oDate)):
            if i > 0:
                if (oDate[i] - oDate[i-1]).seconds > 60:
                    series.append(oDate[l:i])
                    l = i

        series.append(oDate[l:])
        
    return series

###############################################################################



###############################################################################  

def unique(lst):
    
    seen        = set()
    seen_add    = seen.add
    return [x for x in lst if x not in seen and not seen_add(x)]
    
def pick_random(lst):
    
    i = len(lst)-1

    if i < 1:
        return []
    else:
        return lst[random.randint(0,i)]
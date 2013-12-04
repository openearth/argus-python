import re
import urllib2
import datetime

from argus2.filesys import filename

remoteHost = r'http://argus-data.wldelft.nl/sites'
localHost  = r'http://127.0.0.1:6543/sites'

def overview_year_url(station, year):
    
    return '%s/%s/%s/index.html' % (remoteHost, station, year)
    
def overview_day_url(station, oDate, type='snap'):
    
    if re.match('c\d+$', type):
        return oDate.strftime('%s/%s/%%Y/%s/%%j_%%b.%%d/index.html' % (remoteHost, station, type))
    else:
        return oDate.strftime('%s/%s/%%Y/cx/%%j_%%b.%%d/%s.html' % (remoteHost, station, type))
        
def image_url(station, year, url):

    return '/'.join((remoteHost, station, year, url))
    
def local2remote(url):

    return re.sub('^%s' % localHost, remoteHost, url)
    
def extract_image_urls(url, oDate=None):
    'Extract and return all image urls in page'

    regex   = re.compile('<a href="\.\./\.\./(c\d/.+/\d+\.\w+\.\w+\.\d+_\d+_\d+_\d+\.\w+\.\d+\.\w+\.c\d+\.\w+\.jpg)">');
    content = read_url_contents(url)

    if content != None:
        urls = regex.findall(content)
        
        if type(oDate) is datetime.datetime or type(oDate) is datetime.time:
            
            urls = [url for url in urls if abs((filename.filename2datetime(url) - oDate).seconds) < 60]
        
        return urls
    else:
        return []

def read_url_contents(url):
    'Read entire contents of URL'
    
    regex = re.compile('[Zz]andmotor?')
    if regex.search(url):
        url = get_auth_zm(url)
    
    try:
        urlobj = urllib2.urlopen(url)
        return urlobj.read()
    except:
        return None
        
def get_auth_zm(url):
    
    req = urllib2.Request(url)
    unpw = 'emFtbzpkZWxmbGFuZHNla3VzdA=='
    authheader =  "Basic %s" % unpw
    req.add_header("Authorization", authheader)
    
    return req
import pandas
import struct
import numpy as np
import MySQLdb
import re

from argus2 import filesys

MXNAMES  = [  'UNKNOWN',
              'CELL',
              'STRUCT',
              'LOGICAL',
              'CHAR',
              'VOID',
              'DOUBLE',
              'SINGLE',
              'INT8',
              'UINT8',
              'INT16',
              'UINT16',
              'INT32',
              'UINT32',
              'INT64',
              'UINT64',
              'FUNCTION'  ]
              
MXBYTES  = [0, 0, 0, 1,  1,  0, 8,  4,  1, 1, 2,  2,  4,  4,  8,  8,  0 ]
MXSTRUCT = ['','','','?','c','','d','f','','','h','H','i','I','q','Q','']

MX = pandas.DataFrame({'name'   : MXNAMES,
                       'bytes'  : MXBYTES,
                       'struct' : MXSTRUCT})
                       
host        = ''
username    = ''
password    = ''
database    = 'argus'

connection  = None
c           = None

def connect(self):
    'Create MySQL connection'

    try:
        connection = MySQLdb.connect(host, username, password, database)
    except:
        print 'Connection to MySQL database failed, disabling MySQL-dependent functions'

def get_sites(self):

    sql = 'SELECT * FROM site'
    rs  = _execute(sql)

    return rs

def get_stations(self, site=None):

    sql = 'SELECT * FROM station'

    if not site == None:
        sql = sql + ' WHERE siteID = "%s" OR shortName = "%s"' % (site, site)

    rs = _execute(sql)

    return rs

def get_cameras(self, site=None, station=None):

    sql = 'SELECT * FROM camera'

    if not station == None:
        sql   = sql + ' WHERE stationID = "%s"' % station
    elif not site == None:
        sites = get_stations(site=site)
        sql   = sql + ' WHERE stationID IN ("%s")' % '","'.join(sites['id'])

    rs = _execute(sql)

    return rs

def get_cameraid_from_filename(self, argusfile):

    m = filesys.filename2fileparts(argusfile)

    station = get_stations(site=m['station'])
    cameras = get_cameras(station=station['id'][0])

    camid   = cameras['id'][cameras['seq']==int(re.sub('[^\d]+','',m['camera']))].to_dict().values()[0]

    return camid

def get_distortion(self, camera):

    sql   = 'SELECT K, Dtan, Drad FROM camera WHERE id = "%s"' % camera

    rs    = _execute(sql)

    K     = parse_blob(rs['K'][0])
    Drad  = parse_blob(rs['Drad'][0])
    Dtan  = parse_blob(rs['Dtan'][0])

    # make it compatible with cv2
    kc    = np.vstack((Drad, Dtan))
    kc[2], kc[1] = kc[1], kc[2]

    return (K, kc)

def get_geometry(self, camera):

    sql   = 'SELECT m FROM geometry WHERE cameraID = "%s"' % camera

    rs    = _execute(sql)

    L     = _parse_blob(rs['m'][0])

    # make it compatible with Aarninkhof (2003)
    L     = L.T
    L     = L[[0,1,2,3,7,8,9,10,4,5,6]]
    #L     = L[[7,8,9,10,0,1,2,3,4,5,6]]

    return L

def parse_blob(self, bytes):
    'Parse binary blob from MySQL database'

    (id,)       = struct.unpack('>h', bytes[:2])
    bytes       = bytes[2:]

    (classid,)  = struct.unpack('>i', bytes[:4])
    bytes       = bytes[4:]

    (dims,)     = struct.unpack('>i', bytes[:4])
    bytes       = bytes[4:]

    shape       = struct.unpack('>'+'i'*dims, bytes[:4*dims])
    numel       = np.prod(shape)
    bytes       = bytes[4*dims:]

    b = MX.ix[classid]['bytes']
    s = MX.ix[classid]['struct']

    data        = struct.unpack('<'+s*numel, bytes[:b*numel])
    data        = np.array(data)
    data        = data.reshape(shape).transpose()

    return data

def _execute(self, sql):

    c = connection.cursor()

    c.execute(sql)

    rs      = list(c.fetchall())
    columns = [x[0] for x in c.description]
    rs      = pandas.DataFrame.from_records(rs, columns=columns, coerce_float=True)

    return rs
import pandas
import struct
import numpy as np
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

def parse_blob(bytes):
    'Parse binary blob from MySQL database'

    (id,)       = struct.unpack('>h', bytes[:2])
    bytes       = bytes[2:]

    (classid,)  = struct.unpack('>i', bytes[:4])
    bytes       = bytes[4:]

    (dims,)     = struct.unpack('>i', bytes[:4])
    bytes       = bytes[4:]

    assert dims < 4
    shape       = struct.unpack('>'+'i'*dims, bytes[:4*dims])
    assert shape.size < 100
    numel       = np.prod(shape)
    assert numel < 100
    bytes       = bytes[4*dims:]

    b = MX.ix[classid]['bytes']
    s = MX.ix[classid]['struct']

    data        = struct.unpack('<'+s*numel, bytes[:b*numel])
    data        = np.array(data)
    data        = data.reshape(shape)
    
    # make sure we allways return column vectors
    # to be compatible with the matlab json toolbox
    if sum([n>1 for n in data.shape]) == 1:
    	data = data.flatten()

    return data

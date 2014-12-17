import sqlite3
import decimal
import urllib # for decoding urls
import json

import struct
import re
MXARRAYNAMES = ["UNKNOWN",
                "CELL",
                "STRUCT",
                "LOGICAL",
                "CHAR",
                "VOID",
                "DOUBLE",
                "SINGLE",
                "INT8",
                "UINT8",
                "INT16",
                "UINT16",
                "INT32",
                "UINT32",
                "INT64",
                "UINT64",
                "FUNCTION"]

import numpy as np
import pandas
import pandas.io.sql as psql


import utils
import pyramid

import sqlalchemy
from sqlalchemy.sql  import and_, or_
from sqlalchemy.sql import column
from sqlalchemy.types import TypeDecorator, _Binary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

from zope.sqlalchemy import ZopeTransactionExtension

import virtualmodels

# Session Variables
# Filled from configuration

# Database session
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
# Base to be used to create new models
Base = declarative_base()
# Create a metadata database, bound to the engine
metadata = sqlalchemy.MetaData()


class ExtendedEncoder(json.JSONEncoder):
    """extended encoder with support for arbitrary iterables and decimals"""
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
            # try iterables
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        return super(ExtendedEncoder, self).default(o)

class MexBlob(TypeDecorator):
    """Represents a blob that is really a mex object.

    Usage::

        MexBlob('\x00\x00')

    """

    impl = _Binary

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            # read the magic stuff, not sure what this is....
            assert isinstance(value, bytes)

            (magic, ) = struct.unpack('>h', value[:2])
            value = value[2:]
            # read the class id, assumed double
            (mxclassid,) = struct.unpack('>i', value[0:4])
            value = value[4:]
            mxclass = MXARRAYNAMES[mxclassid]
            assert (mxclass == 'DOUBLE')

            # read the number of dimensions
            (numdims,) = struct.unpack('>i', value[0:4])
            value = value[4:]

            # read the shape
            shape = struct.unpack('>' + 'i'*numdims, value[:(4*numdims)])
            value = value[(4*numdims):]

            # read the data
            values = struct.unpack('<' + 'd'*np.prod(shape), value[:(8*np.prod(shape))])
            value = value[(8*np.prod(shape)):]
            assert len(value) == 0
            arr = np.array(values)
            arr.shape = shape
            return arr.tolist()


def update_metadata(metadata):
    # assume all binaries are mexblobs....
    for table in metadata.tables.values():
        for column in table.columns.values():
            if isinstance(column.type, sqlalchemy.types._Binary):
                column.type = MexBlob()


def get_table(table_name, query):
    # Get the table
    if metadata.tables.has_key(table_name):
        table = metadata.tables[table_name]
        # Build the where clause, default to ''
        where = reduce(and_, (column(key)==value for (key,value) in query.items()),'')
        # Execute the sql
        rs = table.select(where).execute()
        rows = []
        for row in rs:
            rows.append(dict(row.items()))
        return rows
    elif virtualmodels.exists(table_name):
        return virtualmodels.get_table(table_name, **query)
    else:
        raise ValueError('Unknown table [%s]' % table_name)    

def get_tables():
    # Get all tables
    tables = metadata.tables.keys()
    tables.extend(virtualmodels.tables)
    return tables

if __name__ == '__main__':
    import doctest
    doctest.testmod()

This is a copy of [http://publicwiki.deltares.nl/display/ARGUS/REST+API]
h2. Introduction

This document describes the web based api description for an argus compatible image collection.
The goal of the web based api is to provide access to the image archive without a database or shared drive connection and to expose other image archives to  the argus analysis software.

We follow the general [REST|https://en.wikipedia.org/wiki/Representational_state_transfer] based api, where important information has a url.


h2. Table interface.

To support the matlab scripts, which are tightly coupled to the table structure of the mysql database we provide the following interface.

| [http://argus-public.deltares.nl/db/table] | return the overview of tables | (/) |
| [http://argus-public.deltares.nl/db/table/IP] | List all the records in the ip table | (/) |
| [http://argus-public.deltares.nl/db/table/IP/?seq=1] | List all the records in the ip table where seq == 1 | (/) |

This code is implemented in:[https://svn.oss.deltares.nl/repos/openearthtools/trunk/python/applications/argusapi]


h2. Field data interface

Having all information regarding an image (site, station, date, time, camera number, etc.) at hand, it is fairly easy to attach related data from additional resources.
Based on the location of the station (lat, lon) and the date and time, field data like tide elevation, location of the sun and meteorological information from KNMI. The following field data is currently available:

|| url || parameters || data source || implemented ||
| [http://argus-public.deltares.nl/db/field/tide] | lat, lon, dt, \[duration\] | Get tidal elevation from [waterbase|http://opendap.deltares.nl/thredds/catalog/opendap/rijkswaterstaat/waterbase/sea_surface_height/catalog.html] | (/) |
| [http://argus-public.deltares.nl/db/field/sun] | lat, lon, dt, \[duration\] | Get position of the sun and other related parameters from [pyephem|http://rhodesmill.org/pyephem/] | (/) |
| [http://argus-public.deltares.nl/db/field/meteo] | lat, lon, dt, \[duration\] | Get hourly meteorological data from [KNMI|http://opendap.deltares.nl/thredds/dodsC/opendap/knmi/uurgeg/] concerning temperature, rainfall, sunshine, etc. | (/) |
| [http://argus-public.deltares.nl/db/plot/field/...] | lat, lon, dt, \[duration\] | Return plot visualizing data listed above | (x) |

The parameter *dt* is specified as a string with format YYYY-MM-DD HH:SS and the parameter duration is specified as the number of days and can be a fraction. The default duration is 0 and the results for a point in time is returned. For durations larger than zero, the time period *around* the provided datetime is returned.

The Deltares OpenDAP server experiences a bug when requesting data source locations of netCDF resources from the catalog: the URL's are truncated. Therefore the matching of resources to the provided location does not work well for resources from this server (tide and meteo). The resources are currently set to Scheveningen and Hoek van Holland respectively until the problem is solved.


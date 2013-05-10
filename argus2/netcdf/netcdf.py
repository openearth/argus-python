import netCDF4
import os, re, time
import numpy as np

from argus2 import image, filesys

storagePath = ''

ncGroups = ('snap','timex','var','min','max')

def create_netcdf(filename, shape=(0,0), colorspace='RGB', url=''):
    'Create an empty netcdf file'
    
    ncfile = netCDF4.Dataset(filename, 'w', format='NETCDF4')
      
    # create dimensions
    dU          = ncfile.createDimension('u', shape[1])
    dV          = ncfile.createDimension('v', shape[0])
    dChannel    = ncfile.createDimension('channel', len(colorspace))

    # create variables
    vU          = ncfile.createVariable('u','i4',('u',))
    vV          = ncfile.createVariable('v','i4',('v',))
    
    # create groups
    for group in ncGroups:
        ncGroup     = ncfile.createGroup(group)
        vOriginal   = ncGroup.createVariable('original','f4',('v','u','channel',))

    # create attributes
    ncfile.description  = 'Argus image %s' % url
    ncfile.history      = 'Created ' + time.ctime(time.time())
    ncfile.source       = 'Argus Python package by Bas Hoonhout <bas.hoonhout@deltares.nl>'
    
    vU.units            = 'pixels'
    vV.units            = 'pixels'

    # add data
    ncfile.variables['u'] = np.arange(1,shape[1])
    ncfile.variables['v'] = np.arange(1,shape[0])
    
    return ncfile
    
def load_image_from_netcdf(url, plugins=None, slice=1):

    filename = _get_netcdf_filename(url)
    imgtype  = filesys.filename.filename2fileparts(url)['imgtype']
    
    if not os.path.exists(filename):
        if plugins == None:
            save_image_to_netcdf(filesys.url.local2remote(url))
        else:
            return None
        
    ncfile = netCDF4.Dataset(filename, 'r+')
    
    if plugins == None:
        img = ncfile.groups[imgtype].variables['original'][::slice,::slice,:]
    else:
        ncGroup = ncfile.groups[imgtype]
        for plugin in plugins:
            if not plugin in ncGroup.groups.keys():
                return None
            else:
                ncGroup = ncGroup.groups[plugin]
        img = ncGroup.variables['image'][::slice,::slice]
    
    ncfile.close()

    return img
    
def save_image_to_netcdf(url, plugins=None, img=None):

    filename = _get_netcdf_filename(url)
    imgtype  = filesys.filename.filename2fileparts(url)['imgtype']

    if not os.path.exists(filename) or img == None:
        img  = image.load.image_from_url(url)
    
    if not os.path.exists(filename):
        ncfile = create_netcdf(filename, shape=img.shape, url=url)
    else:
        ncfile = netCDF4.Dataset(filename, 'r+')
        
    if plugins != None:
        ncGroup = ncfile.groups[imgtype]
        for plugin in plugins:
            if not plugin in ncGroup.groups.keys():
                ncGroup = ncGroup.createGroup(plugin)
        if not 'image' in ncGroup.variables.keys():
            if len(img.shape)>2:
                ncImage = ncGroup.createVariable('image','f4',('v','u','channel',))
                ncImage[:,:,:] = img
            else:
                ncImage = ncGroup.createVariable('image','f4',('v','u',))
                ncImage[:,:] = img
        else:
            ncImage = ncGroup.variables['image']
            if len(img.shape)>2:
                ncImage[:,:,:] = img
            else:
                ncImage[:,:] = img
    else:
        ncfile.groups[imgtype].variables['original'][:,:,:] = img
        
    ncfile.close()
    
def _get_netcdf_filename(url):

    return os.path.join(storagePath, re.sub('\.\w+\.\w+$','.nc',filesys.filename.url2filename(url)))

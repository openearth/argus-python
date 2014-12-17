import cStringIO
import urllib
import matplotlib

# do not show any images
matplotlib.use('Agg')

import matplotlib.pyplot as plt

def image_from_url(url, slice=0):
  'Get image date from URL'
  
  f = cStringIO.StringIO(urllib.urlopen(url).read())
  img = plt.imread(f, format='jpg')
  
  if slice > 0:
    img = img[::slice,::slice,:]
    
  img = img[:,:,:3]/255.0 # FIXME: ignore alpha
  
  return img
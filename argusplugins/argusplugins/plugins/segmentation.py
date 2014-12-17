from argus import image
from argus import segmentation as seg

###############################################################################
## PLUGIN OPTIONS                                                            ##
###############################################################################

options = { 'method'            : ['slic', 'quickshift', 'felzenszwalb', 'random_walker'],
            'n_segments'        : 200,
            'ratio'             : 20,
            'convert2lab'       : True}
            
viz_options = { 'shuffle'           : False,
                'average'           : False,
                'mark_boundaries'   : False}

###############################################################################
## PLUGIN MAIN PROCEDURE                                                     ##
###############################################################################

def run(img, options):
     
    # determine superpixels
    img = seg.superpixel.get_superpixel(img, **options)

    return img
    
def plot(img, img_plugin, options):
    
    img_plugin = seg.superpixel.plot(img, img_plugin, **options)
    
    return img_plugin

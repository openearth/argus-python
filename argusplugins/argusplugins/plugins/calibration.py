from argus2 import image

###############################################################################
## PLUGIN OPTIONS                                                            ##
###############################################################################

options = {}
viz_options = {}

###############################################################################
## PLUGIN MAIN PROCEDURE                                                     ##
###############################################################################

def run(img, options):
     
    return img
    
def plot(img, img_plugin, options):
    
    return image.plot.plot_image(img_plugin, **options)

#import matplotlib

# do not show any images
#matplotlib.use('Agg')

import matplotlib.pyplot as plt
import io, time
import cStringIO
import numpy as np
import flamingo.rectification

import rest, filename

def plot_image(img, cmap='Set2', dpi=96, slice=0, transparent=True):
    'Plot image data'

    start_time = time.time()
    
    if slice > 0:
        img = img[::slice,::slice] 

    i = float(img.shape[1] + 44)/dpi # correct for "invisible" tick label space
    j = float(img.shape[0] + 17)/dpi

    fig, ax = plt.subplots(figsize=(i,j))

    ax.imshow(img, aspect='normal', cmap=cmap)
    ax.set_axis_off()

    plt.subplots_adjust(left=0., right=1., top=1., bottom=0.)
    plt.tight_layout(pad=0., h_pad=0., w_pad=0.)
    
    end_time = time.time()
    print("Elapsed time was %g seconds" % (end_time - start_time))
    
    imgdata = get_image_data(fig, dpi=dpi)
    
    end_time = time.time()
    print("Elapsed time was %g seconds" % (end_time - start_time))

    return imgdata
  
def get_image_data(fig, dpi=96, axis_only=True, transparent=True):

    imgdata = cStringIO.StringIO()
    #imgdata = io.BytesIO()

    if axis_only:

        extent = fig.axes[0].get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(imgdata, format='png', bbox_inches=extent, pad_inches=0, dpi=dpi, transparent=transparent)

    else:
        fig.savefig(imgdata, format='png', pad_inches=0, dpi=dpi, transparent=transparent)

    imgdata.seek(0)

    return imgdata.read()

def undistort(U, V, center=(0,0), coefs=(0,0), K=np.identity(3), rectification_data=None):

    if rectification_data is not None:
        center = (rectification_data['D_U0'], rectification_data['D_V0'])
        coefs = rectification_data['Drad']
        K = rectification_data['K']

    dU = (U - center[0]) / K[0,0]
    dV = (V - center[1]) / K[1,1]

    r = np.sqrt(dU**2 + dV**2)
    scale = 1. + np.polyval(coefs, r) / r
    scale[np.isnan(scale)] = 1.

    r = r / scale
    scale = 1. + np.polyval(coefs, r) / r
    scale[np.isnan(scale)] = 1.

    U = dU / scale * K[0,0] + center[0]
    V = dV / scale * K[1,1] + center[1]

    return U, V

def undistortOLD(U, V, center=(0,0), coefs=(0,0), rectification_data=None):

    lx = 1.006
    ly = -1.

    if rectification_data is not None:
        center = (rectification_data['D_U0'], rectification_data['D_V0'])
        coefs = (rectification_data['D1'], rectification_data['D2'])

    dU = (U / lx) - center[0]
    dV = (V / ly) - center[1]

    d2 = dU**2 + dV**2;
    scale = 1 + coefs[1] + coefs[0]*d2

    d2 = d2 / scale**2;
    scale = 1 + coefs[1] + coefs[0]*d2

    dU = dU / scale
    dV = dV / scale;

    U = (dU + center[0]) * lx
    V = (dV + center[1]) * ly

#def undistort(U, V, center=(0,0), coefs=(0,0), rectification_data=None):
#
#    if rectification_data is not None:
#        center = (rectification_data['D_U0'], rectification_data['D_V0'])
#        coefs = (rectification_data['D1'], rectification_data['D2'])
#
#    dU = U.astype(np.float32) - center[0]
#    dV = V.astype(np.float32) - center[1]
#    
#    r = np.sqrt(dU**2+dV**2)
#    dr = coefs[0]*r**3 + coefs[1]*r
#    pr = (r - dr) / r
#    pr[np.isnan(pr)] = 1
#    
#    U = (dU * pr) + center[0]
#    V = (dV * pr) + center[1]
#    
#    return U, V

def plot_rectified(images, figsize=(30,20), max_distance=1e4, rotate=True):

    r1 = {}
    r2 = {}

    axs = None
    for i, image in enumerate(images):

        img = rest.get_image(image)
        info = filename.filename2fileparts(image)

        s = info['station']
        c = int(info['camera'])

        if s not in r1.keys():
            r1[s] = rest.get_rectification_data(s)

            if rotate:
                r2[s] = rest.get_rotation_data(s)
            else:
                r2[s] = {'rotation':None, 'translation':None}
    
        H = flamingo.rectification.find_homography(r1[s][c]['UV'], r1[s][c]['XYZ'], r1[s][c]['K'])
        u, v = flamingo.rectification.get_pixel_coordinates(img)
        u, v = undistort(u, v, rectification_data=r1[s][c])
        x, y = flamingo.rectification.rectify_coordinates(u, v, H)
    
        fig, axs = flamingo.rectification.plot.plot_rectified([-x], [y], [img], 
                                                              figsize=figsize,
                                                              max_distance=max_distance,
                                                              axs=axs,
                                                              **r2[s])

    return fig, axs

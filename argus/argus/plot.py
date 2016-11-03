#import matplotlib

# do not show any images
#matplotlib.use('Agg')

import urlparse
import logging
import cStringIO
import numpy as np
import flamingo.rectification
import matplotlib.pyplot as plt

import rest, filename, distortion


logger = logging.getLogger(__name__)


def plot_image(img, cmap='Set2', dpi=96, slice=0, transparent=True):
    'Plot image data'

    if slice > 0:
        img = img[::slice,::slice] 

    i = float(img.shape[1] + 44)/dpi # correct for "invisible" tick label space
    j = float(img.shape[0] + 17)/dpi

    fig, ax = plt.subplots(figsize=(i,j))

    ax.imshow(img, aspect='normal', cmap=cmap)
    ax.set_axis_off()

    plt.subplots_adjust(left=0., right=1., top=1., bottom=0.)
    plt.tight_layout(pad=0., h_pad=0., w_pad=0.)
    
    imgdata = get_image_data(fig, dpi=dpi)
    
    return imgdata


def get_image_data(fig, dpi=96, axis_only=True, transparent=True):

    imgdata = cStringIO.StringIO()
    #imgdata = io.BytesIO()

    if axis_only:

        extent = fig.axes[0].get_window_extent().transformed(
            fig.dpi_scale_trans.inverted())
        fig.savefig(imgdata, format='png',
                    bbox_inches=extent, pad_inches=0,
                    dpi=dpi, transparent=transparent)

    else:
        fig.savefig(imgdata, format='png',
                    pad_inches=0, dpi=dpi,
                    transparent=transparent)

    imgdata.seek(0)

    return imgdata.read()


def plot_rectified(urls, figsize=(30,20),
                   max_distance=1e4, rotate=True, ax=None, slice=1):

    r1 = {}
    r2 = {}

    for i, url in enumerate(urls):

        logger.info('Retrieve image data from %s...', url)
        img = rest.get_image(url)
        info = filename.filename2fileparts(url)

        p = urlparse.urlparse(url)
        s = info['station']
        c = int(info['camera'])

        host = '%s://%s' % (p.scheme, p.netloc)

        if s not in r1.keys():
            logger.info('Retrieve rectification data...')
            r1[s] = rest.get_rectification_data(host, s)

            if rotate:
                logger.info('Retrieve rotation data...')
                r2[s] = rest.get_rotation_data(host, s)
            else:
                r2[s] = {'rotation':None, 'translation':None}

        # undistort gcp's
        logger.info('Undistort GCP\'s...')
        UV = [distortion.undistort([u], [v],
                                   **distortion.get_distortion_data(r1[s][c]))
              for u,v in r1[s][c]['UV']]

        # find homography
        logger.info('Find homography...')
        H = flamingo.rectification.find_homography(UV, r1[s][c]['XYZ'], r1[s][c]['K'])

        # undistort image
        logger.info('Undistort image...')
        u, v = flamingo.rectification.get_pixel_coordinates(img)
        u, v = distortion.undistort(u, v, **distortion.get_distortion_data(r1[s][c]))

        # rectify image
        logger.info('Rectify image...')
        x, y = flamingo.rectification.rectify_coordinates(u, v, H)
    
        # plot image
        logger.info('Plot rectified image...')
        fig, ax = flamingo.rectification.plot.plot_rectified([-x], [y], [img],
                                                             slice=slice,
                                                             figsize=figsize,
                                                             max_distance=max_distance,
                                                             ax=ax,
                                                             **r2[s])

    return fig, ax

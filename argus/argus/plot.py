#import matplotlib

# do not show any images
#matplotlib.use('Agg')

import urlparse
import logging
import cStringIO
import numpy as np
import flamingo.rectification as fr
import matplotlib.pyplot as plt

import rest, filename, distortion


logger = logging.getLogger(__name__)


def plot_image(img, cmap='Set2', dpi=96, slice=0, transparent=True):
    '''Return binary image data without margins

    Parameters
    ----------
    img : numpy.ndarray
        Image matrix
    cmap : str or colormap
        Colormap passed to :func:`imshow` function
    dpi : int
        Resolution of image data
    slice : int
        Slice of image data
    transparent : bool
        Toggle image transparancy

    Returns
    -------
    str
        Binary image string
    
    '''

    if slice > 0:
        img = img[::slice,::slice] 

    i = float(img.shape[1] + 44)/dpi # correct for "invisible" tick label space
    j = float(img.shape[0] + 17)/dpi

    fig, ax = plt.subplots(figsize=(i,j))

    ax.imshow(img, aspect='normal', cmap=cmap)
    ax.set_axis_off()

    plt.subplots_adjust(left=0., right=1., top=1., bottom=0.)
    plt.tight_layout(pad=0., h_pad=0., w_pad=0.)
    
    imgdata = get_image_data(fig, dpi=dpi, transparent=transparent)
    
    return imgdata


def get_image_data(fig, dpi=96, axis_only=True, transparent=True):
    '''Extract binary image data from figure object

    Parameters
    ----------
    fig : matplotlib.pyplot.Figure
        Figure object
    dpi : int
        Resolution of returned image data
    axis_only : bool
        Only return axis contents
    transparent : bool
        Toggle image transparency

    Returns
    -------
    str
        Binary image string

    '''

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
    '''Plot ortho-rectified and merges planview image from set of URL's

    Parameters
    ----------
    urls : list
        List of image URL's
    figsize : 2-tuple
        Figure size
    max_distance : float
        Maximum distance in world-coordinates to include in plot
    rotate : bool
        Rotate image to coordinate reference system
    ax : matplotlib.pyplot.Axes
        Axes to use for plotting
    slice : int
        Image slice

    Returns
    -------
    fig : matplotlib.pyplot.Figure
        Figure object
    ax : matplotlib.pyplot.Axes
        Axes object

    '''

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
        UV = [distortion.undistort([u], [v], **r1[s][c]['rectification'])
              for u,v in r1[s][c]['coordinates']['UV']]

        # find homography
        logger.info('Find homography...')
        H = fr.find_homography(UV,
                               r1[s][c]['coordinates']['XYZ'],
                               r1[s][c]['rectification']['K'])

        # undistort image
        logger.info('Undistort image...')
        u, v = fr.get_pixel_coordinates(img)
        u, v = distortion.undistort(u, v, **r1[s][c]['rectification'])

        # rectify image
        logger.info('Rectify image...')
        x, y = fr.rectify_coordinates(u, v, H)
    
        # plot image
        logger.info('Plot rectified image...')
        fig, ax = fr.plot.plot_rectified([-x], [y], [img],
                                         slice=slice,
                                         figsize=figsize,
                                         max_distance=max_distance,
                                         ax=ax,
                                         **r2[s])

    return fig, ax

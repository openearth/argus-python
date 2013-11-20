import io, time
import matplotlib
import cStringIO

# do not show any images
matplotlib.use('Agg')

import matplotlib.pyplot as plt

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

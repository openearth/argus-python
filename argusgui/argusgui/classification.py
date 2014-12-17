import os
import re
import cPickle as pickle
import matplotlib.pyplot as plt
import numpy as np
from flamingo import segmentation as seg
from flamingo import classification as cls
from flamingo import filesys

def get_segmentation_data(ds, im):
    meta = read_export_file(ds, im, 'meta')

    return {'segments': read_export_file(ds, im, 'segments'),
            'contours': read_export_file(ds, im, 'contours'),
            'nx': meta['superpixel_grid'][0],
            'ny': meta['superpixel_grid'][1],
            'width': meta['image_resolution_cropped'][1],
            'height': meta['image_resolution_cropped'][0]}


def get_classification_data(ds, im):

    fpath = get_image_location(ds, im)

    image = {
        'assignments':[],
        'classes':    [],
        'prediction': [],
        'url':        ''};

    if os.path.exists(fpath):

        # read classification file
        assignments = read_export_file(ds, im, 'classes')
            
        if assignments != None:
            image['assignments'] = assignments
            image['classes']     = [x for x in list(set(assignments)) if not x == None]

        # read model file
        if has_features(ds, im):
            ssvm, catlist = read_model_file(ds)
            if not ssvm == None:
                features = read_export_file(ds, im, 'features')

                if not features == None:

                    X, shp = features
#                    X = cls.classification.get_0d_features(X)
                    X = X.reshape((1,shp[0],shp[1],-1))

                    Y = ssvm.predict(X)[0]

                    Y_lbl = np.empty(Y.shape, dtype='object')
                    for i in range(Y.max()+1):
                        Y_lbl[Y==i] = catlist[i]

                    image['prediction'] = Y_lbl.flatten().tolist()

        image['url'] = '%s/%s' % (ds, 'cropped_%s' % im)

    # read default class file
    defaults = read_default_categories(ds)
    image['classes'].extend([x for x in defaults if x not in image['classes']])

    return image

def create_segmentation_file(ds, im, compactness, n_segments, coherent_segments=True):

    image = {}
    fpath = get_image_location(ds, im)
    if os.path.exists(fpath):
        img = read_image_file(fpath)

        image['width']    = img.shape[1]
        image['height']   = img.shape[0]
        image['segments'] = seg.superpixels.get_superpixel(
            img, compactness=compactness, n_segments=n_segments)
        image['nx'], image['ny'] = seg.superpixels.get_superpixel_grid(
            image['segments'], img.shape[:2])
        image['contours'] = seg.superpixels.get_contours(image['segments'])

        # enforce coherent segments
        if coherent_segments:
            write_export_file(ds, im, 'segments.original', image)
            image['segments'] = seg.postprocess.remove_disjoint(image['segments'])
            image['contours'] = seg.superpixels.get_contours(image['segments'])

        image['segments'] = image['segments'].tolist()
            
        write_export_file(ds, im, 'segments', image['segments'])
        write_export_file(ds, im, 'contours', image['contours'])
        write_export_file(ds, im, 'meta', {'superpixel_grid': (image['nx'],image['ny'])})

    return image

def create_classification_file(ds, im, assignments):
    fpath = get_image_location(ds, im)
    if os.path.exists(fpath):
        write_export_file(ds, im, 'classes', assignments)
        return 0
    return 1

def create_feature_file(ds, im):
    fpath = get_image_location(ds, im)
    if os.path.exists(fpath):

        img = read_image_file(fpath)

        segments = read_export_file(ds, im, 'segments')
        
        if len(segments['contours']) == segments['nx'] * segments['ny']: # FIXME
            features = cls.features.blocks.extract_blocks(img, np.array(segments['segments']))

            # TODO: make features 0d

            write_export_file(ds, im, 'features', (features, (segments['nx'],segments['ny'])))

            return 0

    return 1
    
def create_model_file(ds):

    features = []
    classes  = []
    segments = []

    images = get_image_list(ds)
    for im in images:
        if is_classified(ds, im) and is_segmented(ds, im) and has_features(ds, im):
            features.append(np.array(read_export_file(ds, im, 'features')[0])) # what is this zero doing here??
            classes.append(np.array(read_export_file(ds, im, 'classes')))
            segments.append(np.array(read_export_file(ds, im, 'segments')['segments']))

            # TODO: normalize features

    # TODO: hotstart training
    # ssvm, catlist = read_model_file(ds)
    ssvm = None
    #ssvm, catlist = cls.classification.train_classification(features, classes, segments, ssvm=ssvm)

    write_model_file(ds, ssvm, catlist)

def get_image_location(ds, im):
    return os.path.join(get_image_path(ds),im)

def get_image_list(ds):
    images = []
    if not ds == None:
        fpath = get_image_path(ds)
        if os.path.exists(fpath):
            for im in os.listdir(fpath):
                if im.endswith('.jpg') or im.endswith('.JPG') or \
                   im.endswith('.png') or im.endswith('.PNG') or \
                   im.endswith('.jpeg') or im.endswith('.JPEG'):
                    if not im.startswith('cropped_'):
                        images.append(im)
    return images

def get_image_path(ds):
    return os.path.join(get_dataset_path(),ds)

def get_dataset_path():
    return filesys.get_dataset_path() #os.path.join(os.path.dirname(__file__),'datasets') # FIXME    

def get_dataset_list():
    fpath = get_dataset_path()

    datasets = []
    for fname in os.listdir(fpath):
        if not fname.startswith('.') and os.path.isdir(os.path.join(get_dataset_path(), fname)):
            datasets.append(fname);
    return datasets

def get_export_file(ds, im, ext):
    fpath = get_image_location(ds,im)
    return re.sub('\.[\w\d]+$','.%s.pkl' % ext,fpath)

def read_export_file(ds, im, ext):
    contents = None
    pklfile = get_export_file(ds,im,ext)
    if os.path.exists(pklfile):
        fp = open(pklfile, 'rb')
        contents = pickle.load(fp)
        fp.close()
    return contents

def write_export_file(ds, im, ext, contents):
    pklfile = get_export_file(ds,im,ext)
    fp = open(pklfile, 'wb')
    pickle.dump(contents, fp, pickle.HIGHEST_PROTOCOL)
    fp.close()

def get_model_file(ds):
    return os.path.join(get_image_path(ds), 'ssvm.pkl')

def read_model_file(ds):
    ssvm = None
    catlist = None
    fname = get_model_file(ds)
    if os.path.exists(fname):
        fp = open(fname, 'rb')
        ssvm, catlist = pickle.load(fp)
        fp.close()
    return (ssvm, catlist)

def read_image_file(fpath):
    img = None
    if os.path.exists(fpath):
        fpath_cropped = re.sub('\/([^\/]+)$','/cropped_\g<1>', fpath)
        if not os.path.exists(fpath_cropped):
            img = plt.imread(fpath)
            img = img[8:-8,:,:]
            plt.imsave(fpath_cropped, img)
        else:
            img = plt.imread(fpath_cropped)
    return img

def write_model_file(ds, ssvm, catlist):
    fp = open(get_model_file(ds), 'wb')
    pickle.dump((ssvm, catlist), fp, pickle.HIGHEST_PROTOCOL)
    fp.close()

def read_default_categories(ds):
    return filesys.read_default_categories(ds)
    
def is_classified(ds,im):
    classes = read_export_file(ds,im,'classes')
    if classes != None:
        return None not in classes
    return False

def is_segmented(ds,im):
    pklfile = get_export_file(ds,im,'segments')
    return os.path.exists(pklfile)

def has_features(ds,im):
    pklfile = get_export_file(ds,im,'features')
    return os.path.exists(pklfile)


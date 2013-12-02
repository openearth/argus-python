import numpy as np
import pandas
import skimage.measure
import skimage.feature
#import matplotlib.pyplot as plt
from pystruct import models, learners

def comp_features(data,segments):

    pixelprops = {
                 'area',
                 'coords',
                 'convex_area',
                 'centroid',
                 'equivalent_diameter',
                 'perimeter',
                 'moments_central',
                 'solidity',
                 'euler_number',
                 'extent',
                 'moments_normalized',
                 'eccentricity',
                 'convex_image',
                 'label',
                 'filled_image',
                 'orientation',
                 'major_axis_length',
                 'moments',
                 'image',
                 'filled_area',
                 'bbox',
                 'minor_axis_length',
                 'moments_hu'}
    intensityprops = {
                     'label', 
                     'max_intensity',
                     'mean_intensity',
                     'min_intensity',
                     'weighted_moments_central',
                     'weighted_centroid',
                     'weighted_moments_normalized',
                     'weighted_moments_hu',
                     'weighted_moments'}
    
    # built-in pixel features
    regionprops = skimage.measure.regionprops(segments+1, intensity_image=data.mean(-1))
    features    = [{key:feature[key] for key in pixelprops} for feature in regionprops] # if feature._slice is not None]
    
    # built-in intensity features
    df = pandas.DataFrame(features)
    df = df.set_index('label')
    for channel in range(data.shape[-1]):
        regionprops = skimage.measure.regionprops(segments+1, intensity_image=data[...,channel])
        features    = [{key:feature[key] for key in intensityprops} for feature in regionprops] # if feature._slice is not None]
        df_channel  = pandas.DataFrame(features)
        df_channel  = df_channel.set_index('label')
        df          = pandas.merge(df, 
                                   df_channel, 
                                   how='outer', 
                                   left_index=True, 
                                   right_index=True, 
                                   suffixes=('.%d' % (channel-1,), '.%d' % channel))
                                   
    # Custom features
    features = []
    for i, row in df.iterrows():
        
        feature = row.to_dict()
        feature['label'] = row.name
        """Size is represented by the portion of the image covered by the region"""
        feature['size'] = np.prod(segments.shape)/feature['area']
        
        """Position is represented using the coordinates of the region center of mass normalized by the
        image dimensions"""
        feature["position.n"] = feature['centroid'][0]/segments.shape[0]
        feature["position.m"] = feature['centroid'][1]/segments.shape[1]
        
        """Holeyness is defined as the convex area divided by the area"""
        feature["holeyness"] = feature["convex_area"]/feature["area"]
        data_sp = data[segments==feature["label"]-1,:]
        
        
        """Shape is represented by the ratio of the area to the perimeter squared"""
        # seems to be the same as solidity
        feature["shape"] = feature["area"]/(feature["perimeter"]**2)
    
        """Color"""
        n_channels = data.shape[2]
        minn, minm, maxn, maxm = feature['bbox']
        # Select the pixels that are not in the image
        mask= np.logical_not(feature['image'])[:,:,np.newaxis]
        # Repeat along the channels
        mask_channels = np.repeat(mask, repeats=n_channels, axis=2)
        # Select the image pixels and apply the mask
        data_sp = np.ma.masked_array(data[minn:maxn, minm:maxm,:], mask=mask_channels)
        feature['image_masked'] = data_sp 
        for channel in range(n_channels):
            # N based sampel var
            feature["variance_intensity.%d" % channel] = (feature['image_masked'][...,channel]).var()
        for channel in range(n_channels-1):
            feature["mean_relative_intensity.%d" % channel] = (feature['image_masked'][...,channel].astype('float')/feature['image_masked'].sum(-1)).mean()
            feature["variance_relative_intensity.%d" % channel] = (feature['image_masked'][...,channel].astype('float')/feature['image_masked'].sum(-1)).var()
        for channel in range(n_channels):
            n = 5
            counts, bins = np.histogram(feature['image_masked'][...,channel], bins=np.linspace(0, 255, endpoint=True, num=n+1))
            feature["histogram.%d" % channel] = counts
        for channel in range(n_channels):
            greyprops = skimage.feature.greycomatrix(feature['image_masked'][...,channel], distances=[5,7,11], angles=np.linspace(0,1*np.pi,num=6, endpoint=False))
            for prop in {'contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation', 'ASM'}:
                feature["grey_%s.%d" % (prop, channel)] = skimage.feature.greycoprops(greyprops)
            
        features.append(feature)
    
    df = pandas.DataFrame(features)
    df = df.set_index('label')
    
    # Keep this or make loop to reshape matrix features?
    keys     = features[0].keys()
    selected = [len(np.asarray(feature).shape) == 0 for feature in features[0].values()]
    props0d  = sorted(set(np.array(keys)[np.array(selected)]) - {'label'} )
    features = np.empty((segments.max()+1, len(props0d)))

    for idx, (prop) in enumerate(props0d):
        features[:,idx] = np.asarray([df[prop].get(i) for i in range(1,segments.max()+2)], dtype='float')
    
    return features

def train_classification(features,classes,segments,catlist=[]):
    
    if len(features) != len(classes) | len(features) != len(segments):
        raise Exception("Input arguments should be lists of equal length.")
        
    X = []
    Y = []
    
    if catlist == []:
        for i in range(len(classes)):
            catlist.extend([x for x in np.unique(classes[i]) if x not in catlist])
            
    for k in range(len(features)):
        shp = getSuperpixelGrid(segments[k])
        catlabels = np.empty((np.prod(shp),1), dtype='int')
        for i in range(len(catlabels)):
            catlabels[i] = [j for j, x in enumerate(catlist) if classes[k][i] == x]        
        catlabels = catlabels.ravel()

        X.append(features[k])
        X[k] = X[k].reshape((shp[0],shp[1],X[k].shape[-1]))
        X[k] = X[k][:,:,:]

        Y.append(catlabels)
        Y[k] = Y[k].reshape(shp)
   
    model = models.GridCRF(n_states=len(catlist),
                           n_features=features[0].shape[1])
    
    ssvm = learners.OneSlackSSVM(model, 
                                 verbose=0, 
                                 max_iter=10000)
        
    ssvm.fit(X, Y)
    
    return ssvm, X, Y

def predict_classification(ssvm,data,segments,X):

    Y_predicted = np.array(ssvm.predict(X)).flatten()
    img_classified = np.empty(data.shape[0:2])
    
    for i in range(len(Y_predicted)):
        img_classified[segments==i] = Y_predicted[i]
    
    return img_classified
    
def getSuperpixelGrid(segments):
    '''Return shape of superpixels grid'''
    
    K = segments.max()
    height, width = segments.shape
    superpixelsize = width * height / float(K);
    step = np.sqrt(superpixelsize)
    nx = int(round(width / step))
    ny = int(round(height / step))

    assert(np.max(segments) == nx*ny - 1)
    
    return (ny,nx)
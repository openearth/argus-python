import numpy as np
import pandas
import skimage.measure
import skimage.feature
#import matplotlib.pyplot as plt
from pystruct import models, learners
from argus2 import segmentation

pixelprops = {'area',
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
intensityprops = {'label', 
                  'max_intensity',
                  'mean_intensity',
                  'min_intensity',
                  'weighted_moments_central',
                  'weighted_centroid',
                  'weighted_moments_normalized',
                  'weighted_moments_hu',
                  'weighted_moments'}

def extract_features(data,segments):

    # built-in pixel features
    regionprops = skimage.measure.regionprops(segments+1, intensity_image=data.mean(-1))
    features    = [{key:feature[key] for key in pixelprops} for feature in regionprops]# if feature._slice is not None]
    
    # built-in intensity features
    df = pandas.DataFrame(features)
    df = df.set_index('label')
    for channel in range(data.shape[-1]):
        regionprops = skimage.measure.regionprops(segments+1, intensity_image=data[...,channel])
        features    = [{'%s.%d' %(key,channel):feature[key] for key in intensityprops} for feature in regionprops]# if feature._slice is not None]
        df_channel  = pandas.DataFrame(features)
        df_channel  = df_channel.set_index('label.%d' %(channel))
        df          = pandas.merge(df, 
                                   df_channel, 
                                   how='outer', 
                                   left_index=True, 
                                   right_index=True)
                               
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
        for channel in range(n_channels):
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
    
    return features

def make_features_0d(features):

    keys         = features[0].keys()
    n_segments   = len(features)
    n_values = np.empty(len(keys))
    featdim = []
    for i, (prop) in enumerate(keys):
        featdim.append(np.asarray(features[0][prop]).shape)
        if featdim[i]:
            n_values[i] = np.prod(featdim[i])
        else:
            n_values[i] = 1
    
    feature_list = np.empty(n_segments,n_values.sum())
    featinds = n_values.cumsum()
    keys_0d = []
    
    for idx, (prop) in enumerate(keys):
        feature_list[:,featinds[idx]:featinds[idx+1]] = np.asarray([np.asarray(features[i][prop]).ravel() for i in range(n_segments)], dtype='float')
        if featdim[idx] == 1:
            keys_0d.extend(keys[idx])
        elif len(featdim[idx]) == 1:
            keys_0d.extend([keys[idx] + '_' + str(elem) for elem in range(featdim[idx][0])])
        elif len(featdim[idx]) == 2:
            keys_0d.extend([[keys[idx] + '_' + str(row) + '.' + str(col) for col in range(featdim[idx][1])] for row in range(featdim[idx][0] if featdim[idx] ~= 1]))
        elif len(featdim[idx]) == 3:
            keys_0d.extend([[[keys[idx] + '_' + str(sl) + '.' + str(row) + '.' + str(col) for col in range(featdim[idx][2])] for row in range(featdim[idx][1])] for sl in range(featdim[idx][0])])
    
    return feature_list,keys_0d

def train_classification(features,classes,segments,ssvm=None):
    
    if len(features) != len(classes) or len(features) != len(segments):
        raise Exception("Input arguments should be lists of equal length.")

    X = []
    Y = []
    
    catlist = get_category_list(classes)

    for k in range(len(features)):
        feature_array = make_features_0d(features[k])
        n_segments, n_features = feature_array.shape

        catlabels = np.empty((n_segments,1), dtype='int')
        for i in range(n_segments):
            catlabels[i] = [j for j, x in enumerate(catlist) if classes[k][i] == x]        
        catlabels = catlabels.ravel()
    
        shp = segmentation.superpixel.get_superpixel_grid(segments[k], segments[k].shape)

        X.append(feature_array.reshape((shp[0],shp[1],-1)))
        Y.append(catlabels.reshape(shp))
   
    if ssvm == None:
        model = models.GridCRF(n_states=len(catlist),n_features=n_features)
        ssvm = learners.OneSlackSSVM(model, verbose=0, max_iter=10000)
        ssvm.fit(X, Y)
    else:
        ssvm.fit(X, Y, warm_start=True)

    
    return ssvm, catlist

def predict_classification(ssvm,data,segments,X):

    Y_predicted = np.array(ssvm.predict(X)).flatten()
    img_classified = np.empty(data.shape[0:2])
    
    for i in range(len(Y_predicted)):
        img_classified[segments==i] = Y_predicted[i]
    
    return img_classified
    
def get_category_list(classes):
    catlist = []
    for lst in classes:
        if not lst == None:
            catlist.extend(np.unique(lst))
    catlist = np.unique(catlist)
    return [x for x in catlist if not x == None]

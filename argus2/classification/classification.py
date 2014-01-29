import numpy as np
import pandas
import re
import cPickle as pickle
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
        features    = [{'%s.%d' % (key,channel):feature[key] for key in intensityprops} for feature in regionprops]# if feature._slice is not None]
        df_channel  = pandas.DataFrame(features)
#        df_channel  = df_channel.set_index('label.%d' % (channel))
        df          = pandas.merge(df, 
                                   df_channel, 
                                   how='outer', 
                                   left_index=True, 
                                   right_index=True)
                               
    # custom features
    features = []
    for i, row in df.iterrows():
        
        feature = row.to_dict()
        feature['label'] = row.name
       
        # size is represented by the portion of the image covered by the region
        feature['size'] = np.prod(segments.shape)/feature['area']
        
        # position is represented using the coordinates of the region center of mass normalized by the image dimensions
        feature["position.n"] = feature['centroid'][0]/segments.shape[0]
        feature["position.m"] = feature['centroid'][1]/segments.shape[1]
        
        # holeyness is defined as the convex area divided by the area
        feature["holeyness"] = feature["convex_area"]/feature["area"]
        
        # shape is represented by the ratio of the area to the perimeter squared
        # seems to be the same as solidity
        feature["shape"] = feature["area"]/(feature["perimeter"]**2)
    
        # color
        n_channels = data.shape[2]
        minn, minm, maxn, maxm = feature['bbox']

        # select the pixels that are not in the image
        mask = np.logical_not(feature['image'])[:,:,np.newaxis]

        # repeat along the channels
        mask_channels = np.repeat(mask, repeats=n_channels, axis=2)

        # select the image pixels and apply the mask
        data_sp = np.ma.masked_array(data[minn:maxn, minm:maxm,:], mask=mask_channels)
        feature['image_masked'] = data_sp
        for channel in range(n_channels):

            # N based sample var
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

        # these features depend on superpixel size, so should be normalized. pop for now.
        feature.pop('image_masked')
        feature.pop('coords')
        feature.pop('convex_image')
        feature.pop('filled_image')
        feature.pop('image')
            
        features.append(feature)
    
    return features
    
def extract_features_invariant(data,segments):
	
	# Temporal function to check the effect of using only scale-invariant features
    # built-in pixel features
    regionprops = skimage.measure.regionprops(segments+1, intensity_image=data.mean(-1))
    features    = [{key:feature[key] for key in pixelprops} for feature in regionprops]# if feature._slice is not None]
    
    # built-in intensity features
    df = pandas.DataFrame(features)
    df = df.set_index('label')
    for channel in range(data.shape[-1]):
        regionprops = skimage.measure.regionprops(segments+1, intensity_image=data[...,channel])
        features    = [{'%s.%d' % (key,channel):feature[key] for key in intensityprops} for feature in regionprops]# if feature._slice is not None]
        df_channel  = pandas.DataFrame(features)
#        df_channel  = df_channel.set_index('label.%d' % (channel))
        df          = pandas.merge(df, 
                                   df_channel, 
                                   how='outer', 
                                   left_index=True, 
                                   right_index=True)
                               
    # custom features
    features = []
    for i, row in df.iterrows():
        
        feature = row.to_dict()
        feature['label'] = row.name
       
        # size is represented by the portion of the image covered by the region
        feature['size'] = np.prod(segments.shape)/feature['area']
        
        # position is represented using the coordinates of the region center of mass normalized by the image dimensions
        feature["position.n"] = feature['centroid'][0]/segments.shape[0]
        feature["position.m"] = feature['centroid'][1]/segments.shape[1]
        
        # holeyness is defined as the convex area divided by the area
        feature["holeyness"] = feature["convex_area"]/feature["area"]
        
        # shape is represented by the ratio of the area to the perimeter squared
        # seems to be the same as solidity
        feature["shape"] = feature["area"]/(feature["perimeter"]**2)
    
        # color
        n_channels = data.shape[2]
        minn, minm, maxn, maxm = feature['bbox']

        # select the pixels that are not in the image
        mask = np.logical_not(feature['image'])[:,:,np.newaxis]

        # repeat along the channels
        mask_channels = np.repeat(mask, repeats=n_channels, axis=2)

        # select the image pixels and apply the mask
        data_sp = np.ma.masked_array(data[minn:maxn, minm:maxm,:], mask=mask_channels)
        feature['image_masked'] = data_sp
        for channel in range(n_channels):

            # N based sample var
            feature["variance_intensity.%d" % channel] = (feature['image_masked'][...,channel]).var()

        for channel in range(n_channels):
            feature["mean_relative_intensity.%d" % channel] = (feature['image_masked'][...,channel].astype('float')/feature['image_masked'].sum(-1)).mean()
            feature["variance_relative_intensity.%d" % channel] = (feature['image_masked'][...,channel].astype('float')/feature['image_masked'].sum(-1)).var()

        for channel in range(n_channels):
            n = 5
            counts, bins = np.histogram(feature['image_masked'][...,channel], bins=np.linspace(0, 255, endpoint=True, num=n+1))
            feature["histogram.%d" % channel] = counts
		
		# These texture features are not scale-invariant! Use Gabor-filtering instead.
        #for channel in range(n_channels):
        #    greyprops = skimage.feature.greycomatrix(feature['image_masked'][...,channel], distances=[5,7,11], angles=np.linspace(0,1*np.pi,num=6, endpoint=False))
        #    for prop in {'contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation', 'ASM'}:
        #        feature["grey_%s.%d" % (prop, channel)] = skimage.feature.greycoprops(greyprops)

        # these features depend on superpixel size, so should be normalized. pop for now.
        feature.pop('image_masked')
        feature.pop('coords')
        feature.pop('convex_image')
        feature.pop('filled_image')
        feature.pop('image')
        
        # Normalization to make all features scale-invariant
        feature["histogram"] = feature["histogram"]/feature["area"] # Normalize the histogram before the superpixel area is normalized itself, see below
        
        length_features = ["equivalent_diameter","major_axis_length","minor_axis_length","perimeter"]	# Normalize with square-root of image area
        area_features = ["area","convex_area","filled_area"]	# Normalize with image area
        coordinate_features = ["centroid","weighted_centroid"]	# Normalize with image width and height
        
        for lfeat in length_features:
        	feature[lfeat] = feature[lfeat]/np.sqrt(data.size)
        
        for afeat in area_features:
        	feature[afeat] = feature[afeat]/data.size
        	
        for cfeat in coordinate_features:
        	feature[cfeat] = feature[cfeat]/np.array(data.shape)[[0,1]]
        
        feature["bbox"][[0,2]] = feature["bbox"][[0,2]]/data.shape[0]
        feature["bbox"][[1,3]] = feature["bbox"][[0,2]]/data.shape[1]
        
        # These features already have a normalized counterpart from the regionprops function
        feature.pop("moments")
        feature.pop("moments_central")
        feature.pop("weighted_moments")
        feature.pop("weighted_moments_central")
        
        feature.pop("size") # This is the inverse of the normalized area feature, makes less sense
        feature.pop("position.m") # Equal to normalized centroid
        feature.pop("position.n") # Equal to normalized centroid
        
        # Append to features list
        features.append(feature)
    
    return features

def make_features_0d(features):
    '''convert all items in each matrix feature into individual features'''

    features_lin = [{} for i in range(len(features))]
    for i, feature in enumerate(features):
        for name, value in feature.iteritems():
            arr = np.asarray(value)
            if np.prod(arr.shape) > 1:
                for j, item in enumerate(arr.ravel()):
                    features_lin[i]['%s.%d' % (name, j)] = item
            else:
                features_lin[i][name] = value

    return features_lin
                
#    keys = features[0].keys()
#    n_segments = len(features)
#    n_values = np.empty(len(keys))
#    featdim = []
#
#    for i, prop in enumerate(keys):
#        featdim.append(np.asarray(features[0][prop]).shape)
#        if featdim[i]:
#            n_values[i] = np.prod(featdim[i])
#        else:
#            n_values[i] = 1
#    
#    feature_list = np.empty((n_segments,n_values.sum()))
#    featinds = n_values.cumsum()
#    featinds = np.append(0,featinds)
#    keys_0d = []
#       
#    for idx, prop in enumerate(keys):
#        try:
#            feature_list[:,featinds[idx]:featinds[idx+1]] = np.asarray(
#                [np.asarray(features[i][prop], dtype='float').ravel() for i in range(n_segments)])
#
#            # BAS: why not use ravel/flatten?
#            if n_values[idx] == 1:
#                keys_0d.append(keys[idx])
#            elif len(featdim[idx]) == 1:
#                keys_0d.extend(keys[idx] + '_' + str(elem) for elem in range(featdim[idx][0]))
#            elif len(featdim[idx]) == 2:
#                keys_0d.extend(keys[idx] + '_' + str(row) + '.' + str(col) for col in range(featdim[idx][1]) for row in range(featdim[idx][0]) if featdim[idx] != 1)
#            elif len(featdim[idx]) == 3:
#                keys_0d.extend(keys[idx] + '_' + str(sl) + '.' + str(row) + '.' + str(col) for col in range(featdim[idx][2]) for row in range(featdim[idx][1]) for sl in range(featdim[idx][0]))
#        except:
#            print idx
#    
#    return feature_list,keys_0d
    
def get_feature_stats(feature_files):
    '''extract feature statistics from feature files'''

    istat = []
    for i, fname in enumerate(feature_files):

        # open feature file
        fp = open(fname,'rb')
        features = pickle.load(fp)
        fp.close()

        df = pandas.DataFrame(features)
        df = df.set_index('label')

        # extract image statistics
        istat.append(pandas.DataFrame({
            'img':fname,
            'avg':df.mean(),
            'var':df.var(),
            'min':df.min(),
            'max':df.max(),
            'sum':df.sum(),
            'n':df.shape[0]}))

    istat = pandas.concat(istat)
    istat.index.name = 'feature'
    istat = istat.set_index('img', append=True)

    # number of items
    ilen = istat['n'].sum(level='feature')

    # combined weighed average
    avg = (istat['avg'] * istat['n']).sum(level='feature') / ilen

    # create repeated series of combined weighed average (FIXME)
    avg_r = []
    for fname in feature_files:
        df = pandas.DataFrame({'avg':avg})
        df['img'] = fname
        avg_r.append(df)
    avg_r = pandas.concat(avg_r)
    avg_r = avg_r.set_index('img', append=True)

    # combined weighed variance
    var = (istat['n'] * (istat['var'] + (istat['avg'] - avg_r['avg'])**2)).sum(level='feature') / ilen

    fstat = pandas.DataFrame({'avg':avg, 'var':var})
    fstat['min'] = istat['min'].min(level='feature')
    fstat['max'] = istat['max'].max(level='feature')
    fstat['sum'] = istat['sum'].sum(level='feature')

    return istat, fstat

#        if i == 0:
#            image_stats = np.empty((len(feature_files),6,features.shape[1]))
#        
#        # BAS: why not use a dataframe for clarity??
#        image_stats[i,0,:] = features.mean(axis = 0)
#        image_stats[i,1,:] = features.var(axis = 0)
#        image_stats[i,2,:] = features.shape[0]
#        image_stats[i,3,:] = np.nanmin(features,axis = 0)
#        image_stats[i,4,:] = np.nanmax(features,axis = 0)
#        image_stats[i,5,:] = np.sum(np.isnan(features),axis = 0)
#        
#    n_samp = image_stats[:,2,0].sum()
#
#    # BAS: dataframe??
#    feature_stats = np.empty((features.shape[1],5))
#    
#    for i in range(features.shape[1]):
#        
#        # combined mean
#        feature_stats[i,0] = np.sum(image_stats[:,0,i] * image_stats[:,2,i])/n_samp
#        
#        # combined variance, see http://www.emathzone.com/tutorials/basic-statistics/combined-variance.html
#        feature_stats[i,1] = np.sum(image_stats[:,2,i] * (image_stats[:,1,i] + (image_stats[:,0,i] - feature_stats[i,0])**2))/n_samp
#
#        feature_stats[i,2] = np.min(image_stats[:,3,i])
#        feature_stats[i,3] = np.max(image_stats[:,4,i])
#        feature_stats[i,4] = np.sum(image_stats[:,5,i])
        
def normalize_features(feature_files, fstat):
    '''iterate over all feature files and convert to standard normal space. write to new pickle files.'''

    for fname in feature_files:

        fp = open(fname,'rb')
        features = pickle.load(fp)
        fp.close()

        # convert to standard normal distribution: (x - mu)/sigma
        df = pandas.DataFrame(features)
        df = df.set_index('label')
        df_normalized = (df - fstat['avg']) / fstat['var'].apply(np.sqrt)

        # dump to new pickle file
        fid = open(re.sub('\.[^\.]+$','_normalized\g<0>',fname), 'wb')
        pickle.dump(df_normalized.T.to_dict().values(),fid)
        fid.close()

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

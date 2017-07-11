from pyramid.security import authenticated_userid
from pyramid.view import view_config, forbidden_view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPUnauthorized

import os
import numpy as np

from flamingo import filesys

import classification
import queue

queue.clean_queue()

@view_config(route_name='gui_home', renderer='templates/monitor.pt')
def gui_home(request):
    return {}

@view_config(route_name='gui_classification', renderer='templates/classification.pt')
def gui_classification(request):
    return {}

@view_config(route_name='gui_compare', renderer='templates/compare.pt')
def gui_compare(request):
    return {}

@view_config(route_name='gui_test', renderer='templates/test.pt')
def gui_test(request):
    return {}

@view_config(route_name='train', renderer='jsonp')
def view_train(request):
    ds = request.matchdict.get('dataset', None)

    queue.add_to_queue(
        'Fitting model to data...', 
        classification.create_model_file, ds)

    return 0

@view_config(route_name='queue', renderer='jsonp')
def view_queue(request):
    return queue.get_queue()

@view_config(route_name='compare', renderer='jsonp')
def view_compare(request):
    datasets = request.params.get('datasets', None)

    if datasets == None:
        datasets = classification.get_dataset_list()
    else:
        datasets = datasets.split(',')

    images = None
    for ds in datasets:
        im = set(classification.get_image_list(ds))
        if images == None:
            images = im
        else:
            images = images & im

    comparison = {}
    for im in images:
        assignments = []
        for ds in datasets:
            assignment = np.array(classification.get_classification_data(ds,im)['assignments'])

            if len(assignment) > 0:
                if len(assignments) > 0:
                    assignments = np.vstack((assignments, assignment))
                else:
                    assignments = assignment.reshape((1,-1))

        if len(assignments) > 0:
            comparison[im] = [bool(x) for x in np.all(assignments == assignments[0,:], axis=0)]

    return (comparison, datasets)

@view_config(route_name='datasets', renderer='jsonp')
def view_datasets(request):
    return classification.get_dataset_list()

@view_config(route_name='dataset', renderer='jsonp')
def view_dataset(request):
    ds = request.matchdict.get('dataset', None)

    dataset = []
    images  = classification.get_image_list(ds)
    for im in images:
        dataset.append({
                'file':im,
                'isclassified':classification.is_classified(ds,im)});

    return dataset

@view_config(route_name='image', request_method='POST', renderer='jsonp')
def view_classify(request):
    
    ds = request.matchdict.get('dataset', None)
    im = request.matchdict.get('image', None)

    if not ds == None and not im == None:
        
        return classification.create_classification_file(
            ds, im, request.json_body['assignments'])
 
    return 1

@view_config(route_name='image', request_method='GET', renderer='jsonp')
def view_image(request):

    ds = request.matchdict.get('dataset', None)
    im = request.matchdict.get('image', None)

    compactness = int(request.params.get('compactness', 20))
    n_segments  = int(request.params.get('n_segments', 600))

    force_segmentation = request.params.get('force_segmentation', 'false') in ['true','1',1,True]

    image = {}
    if not ds == None and not im == None:

        if not force_segmentation:
            image = classification.get_segmentation_data(ds, im)

        if not image:
            force_segmentation = True

        if force_segmentation:
            image = classification.create_segmentation_file(
                ds, im, compactness, n_segments)

        if force_segmentation or not classification.has_features(ds, im):
            pass
#            queue.add_to_queue(
#                'Extracting features for "%s"...' % im,
#                classification.create_feature_file, ds, im)
        
        image.update(classification.get_classification_data(ds,im))

    keys = request.params.get('keys',None)
    if keys == None:
        return image
    else:
        return {k:v for k,v in image.iteritems() if k in keys.split(',')}

@forbidden_view_config()
def forbidden_view(request):
    res = HTTPUnauthorized()
    res.www_authenticate = 'Basic realm="Secure Area"'
    return res
    
def _reconstructImageUrl(request):

    url = url.image_url(request.matchdict['site'],
                        request.matchdict['year'], 
                        '/'.join((request.matchdict['camera'], 
                                  request.matchdict['day'],
                                  request.matchdict['file'])))
    return url

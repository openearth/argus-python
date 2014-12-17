import os
import plugins

import numpy as np
import urllib

from argus import image, filesys

def run_plugins(plugins, filename, request, plot=True):
    'Run multiple plugins in sequence'
    
    url        = filesys.filename.filename2url(filename)
    img        = image.load.image_from_url(url)
    img_plugin = img.copy()

    for plugin in plugins:
        img_plugin = run_plugin(plugin, url, img_plugin, request)
    
    if plot:
        mod         = get_plugin_module(plugins[-1])
        options     = read_options(request, mod.viz_options)
        options.update({'slice':int(request.params.get('slice',1))})
        img_plugin  = mod.plot(img, img_plugin, options)
    
    return img_plugin
    
def run_plugin(plugin, url, img, request):
    'Run a specific plugin'
  
    mod     = get_plugin_module(plugin)

    # read configuration options
    options = read_options(request, mod.options)

    # run plugin
    img     = mod.run(img, options)

    return img
    
def get_plugins():
    'Return a list of available plugins'

#    files   = os.listdir(os.path.join(os.getcwd(), 'argusplugins/plugins'))
    files   = os.listdir('/home/hoonhout/Checkouts/OpenEarthTools/python/applications/argusplugins/argusplugins/plugins') # FIXME
    plugins = []

    for i, file in enumerate(files):
        if file[0] != '_' and file[-3:] == '.py':
            plugins.append(file[:-3])

    return plugins
    
def get_plugin_options(plugin, request=None):
    'Return a dictionairy of available options for a given plugin'
    
    if plugin != "":
        mod = get_plugin_module(plugin)
        return mod.options
    else:
        return []

def get_plugin_vizoptions(plugin, request=None):
    'Return a dictionairy of available vizualization options for a given plugin'
    
    if plugin != "":
        mod = get_plugin_module(plugin)
        return mod.viz_options
    else:
        return []
        
def get_plugin_module(plugin):
    'Check and return plugin module'

    try:
        mod = plugins.__getattribute__(plugin)
    except:
        raise ValueError('Unknown plugin [%s]' % plugin)

    # check if necessary methods and attributes are available
    if not hasattr(mod, 'options') or callable(getattr(mod, 'options')):
        raise NotImplementedError('Plugin "options" attribute not implemented [%s]' % plugin)

    if not hasattr(mod, 'run') or not callable(getattr(mod, 'run')):
        raise NotImplementedError('Plugin "run" method not implemented [%s]' % plugin)
        
    if not hasattr(mod, 'viz_options') or callable(getattr(mod, 'viz_options')):
        raise NotImplementedError('Plugin "viz_options" attribute not implemented [%s]' % plugin)
        
    if not hasattr(mod, 'plot') or not callable(getattr(mod, 'plot')):
        raise NotImplementedError('Plugin "plot" method not implemented [%s]' % plugin)

    return mod
    
def read_options(request, defaults):
    'Overwrite default option values with requested values'

    options = defaults.copy()

    for k, v in defaults.iteritems():

        if type(v) is list:
            v = v[0]

        if request != None:
            value = request.params.get(k, v)
        else:
            value = v

        if type(v) is int:
            value = int(value)
        elif type(v) is str:
            value = str(value)
        elif type(v) is bool:
            value = value == 'true'
#            value = bool(value)
        else:
            raise ValueError('Unknown option type')

        if value == '' and options.has_key(k):
            pass
        else:
            options[k] = value

    return options

def get_selected(options, selected):

    option_dict = {}

    for option in selected:
        if options.has_key(option):
            option_dict[option] = options[option]

    return option_dict

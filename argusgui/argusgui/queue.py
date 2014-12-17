from multiprocessing import Queue, Lock, Process
import cPickle as pickle
import tempfile
import hashlib
import os

queue = Queue()
lock  = Lock()

def add_to_queue(msg, fcn, *args):
    if not queue.full():
        hash = make_fcn_hash(fcn, *args)
        fname = get_hash_file(hash)

        if not os.path.exists(fname):

            item = {
                'hash':hash,
                'fcn':fcn,
                'msg':msg,
                'args':args }
          
            fp = open(fname, 'wb')
            pickle.dump(item, fp)
            fp.close()

            queue.put(hash)

            if lock.acquire(False):
                Process(target=run_from_queue).start()
            
def run_from_queue():
    hash = queue.get()
    fname = get_hash_file(hash)

    if os.path.exists(fname):
        fp = open(fname, 'rb')
        item = pickle.load(fp)
        fp.close()

        fcn  = item['fcn']
        args = item['args']

        fcn(*args)
        
        os.remove(fname)

    if not queue.empty():
        run_from_queue()
    else:
        lock.release()

def get_queue():

    queue = {}
    for fname in os.listdir(get_hash_path()):
        if fname.endswith('.pkl'):
            fp = open(os.path.join(get_hash_path(), fname), 'rb')
            item = pickle.load(fp)
            fp.close()

            queue[item['hash']] = {k:v for k,v in item.iteritems() if k not in ['fcn']}

    return queue

def clean_queue():
    for fname in os.listdir(get_hash_path()):
        if fname.endswith('.pkl'):
            os.remove(os.path.join(get_hash_path(), fname))

def get_hash_path():
    fpath = os.path.join(tempfile.gettempdir(), 'argusgui_hash')
    if not os.path.exists(fpath):
        os.mkdir(fpath)
    return fpath

def get_hash_file(hash):
    return os.path.join(get_hash_path(), '%s.pkl' % hash)

def make_fcn_hash(fcn, *args):

    m = hashlib.md5()
    m.update(fcn.__name__)

    for arg in args:
        m.update(str(arg))

    return m.hexdigest()

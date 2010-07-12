import os
from os import path
import hashlib
def hash_file(filename):
    '''
    hash = hash_file(filename)

    Computes hash for contents of `filename`
    '''
    hash = hashlib.md5()
    input = file(filename)
    s = input.read(4096)
    while s:
        hash.update(s)
        s = input.read(4096)
    content = hash.hexdigest()
    return content
    
def props_for(filename):
    '''
    props = props_for(filename)

    Properties for `filename`
    '''
    st = os.stat(filename)
    return st.st_mode, st.st_uid, st.st_gid, st.st_mtime


def merge(origin, dest):
    '''
    for op,args in merge(origin, dest);
        op(*args)

    Attempt to merge directories `origin` and `dest`
    '''
    filequeue = os.listdir(origin)
    while filequeue:
        fname = filequeue.pop()
        ofname = path.join(origin, fname)
        dfname = path.join(dest, fname)
        if not path.exists(dfname):
            yield os.rename, (ofname, dfname)
            continue
        if hash_file(ofname) != hash_file(dfname):
            print 'Content differs: %s' % (fname)
            continue
        if props_for(ofname) != props_for(dfname):
            print 'Flags differ: %s' % (fname) 
            continue
        yield os.unlink, (ofname,)

def main(argv):
    origin = argv[1]
    dest = argv[2]
    for op,args in merge(origin, dest):
        op(*args)


if __name__ == '__main__':
    import sys
    main(sys.argv)


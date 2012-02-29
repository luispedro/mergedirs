import os
from os import path
import hashlib

__version__ = '0.1'
_usage_simple = '''
%s <origin> <dest>

Merges directory <origin> into directory <dest>
'''
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


def merge(origin, dest, options):
    '''
    for op,args in merge(origin, dest);
        op(*args)

    Attempt to merge directories `origin` and `dest`

    Parameters
    ----------
    origin : str
        path to origin
    dest : str
        path to destination
    options : options object
    '''
    filequeue = os.listdir(origin)
    while filequeue:
        fname = filequeue.pop()
        ofname = path.join(origin, fname)
        dfname = path.join(dest, fname)
        if not path.exists(dfname):
            if not options.remove_only:
                yield os.rename, (ofname, dfname)
            continue
        if path.isdir(ofname):
            filequeue.extend(path.join(fname,ch) for ch in os.listdir(ofname))
            continue
        if not options.ignore_flags and props_for(ofname) != props_for(dfname):
            print 'Flags differ: %s' % (fname)
            continue
        if hash_file(ofname) != hash_file(dfname):
            print 'Content differs: %s' % (fname)
            continue
        yield os.unlink, (ofname,)

def main(argv):
    from optparse import OptionParser
    parser = OptionParser(usage=_usage_simple % argv[0], version=__version__)
    parser.add_option('--ignore-flags', action='store_true', dest='ignore_flags')
    parser.add_option('--remove-only', action='store_true', dest='remove_only')
    options,args = parser.parse_args(argv)
    if len(args) < 3:
        print _usage_simple % argv[0]
        sys.exit(1)
    _, origin, dest = args
    for op,args in merge(origin, dest, options):
        op(*args)


if __name__ == '__main__':
    import sys
    main(sys.argv)


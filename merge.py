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
    #print 'hashing(%s)...' % filename
    hash = hashlib.md5()
    with open(filename) as input:
        s = input.read(4096)
        while s:
            hash.update(s)
            s = input.read(4096)
    return hash.hexdigest()

def hash_recursive(directory):
    '''
    hash = hash_recursive(directory)

    Computes a hash recursively
    '''
    from os import listdir, path
    files = listdir(directory)
    files.sort()

    hash = hashlib.md5()
    for f in files:
        p = path.join(directory, f)
        if path.isdir(p):
            hash.update(hash_recursive(p))
        elif path.isfile(p):
            hash.update(hash_file(p))
        else:
            raise OSError("Cannot handle files such as `%s`" % p)
    return hash.hexdigest()

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
        try:
            if not path.exists(dfname):
                if not options.remove_only:
                    if options.verbose:
                        print 'mv', ofname, dfname
                    yield os.rename, (ofname, dfname)
                elif options.verbose:
                    print '#mv', ofname, dfname
            elif path.isdir(ofname):
                filequeue.extend(path.join(fname,ch) for ch in os.listdir(ofname))
            elif not path.isfile(ofname):
                print 'Ignoring non-file non-directory: %s' % ofname
            elif not options.ignore_flags and props_for(ofname) != props_for(dfname):
                print 'Flags differ: %s' % (fname)
            elif path.isdir(dfname):
                print 'File `%s` matches directory `%s`' % (ofname, dfname)
            elif not path.isfile(dfname):
                print 'File `%s` matches non-file `%s`' % (ofname, dfname)
            elif hash_file(ofname) != hash_file(dfname):
                print 'Content differs: %s' % (fname)
            else:
                if options.verbose:
                    print 'rm', ofname
                yield os.unlink, (ofname,)
        except IOError, e:
            import sys
            print >>sys.stderr, 'Error accessing `%s`/`%s`: %s' % (ofname, dfname, e)
            if not options.continue_on_error:
                return


def main(argv):
    from optparse import OptionParser
    parser = OptionParser(usage=_usage_simple % argv[0], version=__version__)
    parser.add_option('--ignore-flags', action='store_true', dest='ignore_flags')
    parser.add_option('--remove-only', action='store_true', dest='remove_only')
    parser.add_option('--verbose', action='store_true', dest='verbose')
    parser.add_option('--continue-on-error', action='store_true', dest='continue_on_error')
    parser.add_option('--mode',
                        action='store',
                        dest='mode',
                        default='merge',
                        help='What to do [merge/hash]')
    options,args = parser.parse_args(argv)
    if options.mode == 'merge':
        if len(args) < 3:
            from sys import exit
            print _usage_simple % argv[0]
            exit(1)
        _, origin, dest = args
        for op,args in merge(origin, dest, options):
            try:
                op(*args)
            except IOError, err:
                import sys
                print >>sys.stderr, 'Error executing ', op, args, err
                if not options.continue_on_error:
                    break
    elif options.mode == 'hash':
        if len(args) != 2:
            from sys import exit
            print 'hash mode needs path'
            exit(1)
        _,path = args
        h = hash_recursive(path)
        print '{:<24} {}'.format(path, h)


if __name__ == '__main__':
    import sys
    main(sys.argv)


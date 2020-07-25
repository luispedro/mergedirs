import os
from os import path
import shutil
import hashlib
from .flags import set_oldest

__version__ = '0.1'
_usage_simple = '''
{argv0} <origin> <dest>

Merges directory <origin> into directory <dest>

{argv0} --mode=hash [FLAGS] <directory>

Hash a directory (recursively)
'''
def same_file_content(file1, file2):
    '''same_file_content(file1: filepath, file2: filepath) -> bool

    Checks if `file1` and `file2` have the same content

    Parameters
    ----------
    file1 : filepath
    file2 : filepath

    Returns
    -------
    is_same : bool
    '''
    bufsize = 8192
    with open(file1, 'rb') as input1:
        with open(file2, 'rb') as input2:
            while True:
                data1 = input1.read(bufsize)
                data2 = input2.read(bufsize)
                if data1 != data2:
                    return False
                if not data1:
                    return True

def hash_file(filename):
    '''
    hash = hash_file(filename)

    Computes hash for contents of `filename`
    '''
    #print('hashing({})...'.format(filename))
    hash = hashlib.md5()
    with open(filename, 'rb') as input:
        s = input.read(4096)
        while s:
            hash.update(s)
            s = input.read(4096)
    return hash.hexdigest().encode('ascii')

def hash_recursive(directory):
    '''
    hash = hash_recursive(directory)

    Computes a hash recursively
    '''
    from os import listdir, readlink
    files = listdir(directory)
    files.sort()

    hash = hashlib.md5()
    for f in files:
        p = path.join(directory, f)
        if path.islink(p):
            hash.update('link')
            hash.update(readlink(p))
        elif path.isdir(p):
            hash.update(hash_recursive(p))
        elif path.isfile(p):
            hash.update(hash_file(p))
        else:
            raise OSError("Cannot handle files such as `{}`".format(p))
    return hash.hexdigest().encode('ascii')

def props_for(filename):
    '''
    props = props_for(filename)

    Properties for `filename`
    '''
    st = os.stat(filename)
    return st.st_mode, st.st_uid, st.st_gid, st.st_mtime


class Action(object):
    def __init__(self, f, args):
        self.f = f
        self.args = args

    def run(self):
        self.f(*self.args)

def merge(origin, dest, options):
    '''
    for op in merge(origin, dest);
        op.run()

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
            if not path.lexists(dfname):
                if not options.remove_only:
                    if options.verbose:
                        print('mv {} {}'.format(ofname, dfname))
                    yield Action(shutil.move, (ofname, dfname))
                elif options.verbose:
                    print('#mv {} {}'.format(ofname, dfname))
            elif path.islink(ofname):
                print('Ignoring link: {}'.format(ofname))
            elif path.isdir(ofname):
                if options.ignore_git and fname == '.git':
                    print('Skipping .git directory: {}'.format(ofname))
                else:
                    filequeue.extend(sorted(path.join(fname,ch) for ch in os.listdir(ofname)))
            elif not path.isfile(ofname):
                print('Ignoring non-file non-directory: {}'.format(ofname))
            elif not options.ignore_flags and props_for(ofname) != props_for(dfname):
                print('Flags differ: {}'.format(fname))
            elif path.isdir(dfname):
                print('File `{}` matches directory `{}`'.format(ofname, dfname))
            elif not path.isfile(dfname) and not (options.follow_links and path.islink(dfname)):
                print('File `{}` matches non-file `{}`'.format(ofname, dfname))
            elif not same_file_content(ofname, dfname):
                print('Content differs: {}'.format(fname))
            else:
                if options.verbose:
                    print('rm {}'.format(ofname))
                if options.set_oldest:
                    yield Action(set_oldest, (ofname,dfname))
                yield Action(os.unlink, (ofname,))
        except IOError as e:
            import sys
            sys.stderr.write('Error accessing `{}`/`{}`: {}\n'.format(ofname, dfname, e))
            if not options.continue_on_error:
                return

def parse_options(argv):
    from optparse import OptionParser
    parser = OptionParser(usage=_usage_simple.format(argv0=argv[0]), version=__version__)
    parser.add_option('--ignore-flags', action='store_true', dest='ignore_flags')
    parser.add_option('--ignore-git', action='store_true', dest='ignore_git')
    parser.add_option('--remove-only', action='store_true', dest='remove_only')
    parser.add_option('--verbose', action='store_true', dest='verbose')
    parser.add_option('--continue-on-error', action='store_true', dest='continue_on_error')
    parser.add_option('--follow-links', action='store_true', dest='follow_links', help='Follow links to content (destination)')
    parser.add_option('--set-oldest', action='store_true', dest='set_oldest', help='Set mtime & atime to oldest of origin/destination')
    parser.add_option('--mode',
                        action='store',
                        dest='mode',
                        default='merge',
                        help='What to do [merge/hash]')
    return parser.parse_args(argv)

def main(argv):
    options,args = parse_options(argv)
    if options.set_oldest and not options.ignore_flags:
        from sys import exit,stderr
        stderr.write("--set-oldest does not make sense without --ignore-flags\n")
        exit(1)
    if options.mode == 'merge':
        if len(args) < 3:
            from sys import exit
            print(_usage_simple.format(argv0=argv[0]))
            exit(1)
        _, origin, dest = args
        if path.abspath(origin) == path.abspath(dest):
            from sys import exit
            print('origin and dest are the same.')
            exit(2)
        for op in merge(origin, dest, options):
            try:
                op.run()
            except IOError as err:
                import sys
                sys.stderr.write('Error executing {} {}: {}\n'.format(op.f, op.args, err))
                if not options.continue_on_error:
                    break
    elif options.mode == 'hash':
        if len(args) < 2:
            from sys import exit
            print('hash mode needs path')
            exit(1)
        for arg in args[1:]:
            h = hash_recursive(arg)
            print('{:<24} {}'.format(arg, h.decode('ascii')))


if __name__ == '__main__':
    import sys
    main(sys.argv)


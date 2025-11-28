import os
import sys
from os import path
import shutil
import hashlib
import collections
from .flags import set_oldest
from .mergedirs_version import __version__

_usage_simple = '''
{argv0} <origin> <dest>

Merges directory <origin> into directory <dest>

{argv0} --mode=hash [FLAGS] <directory>

Hash a directory (recursively)
'''


def same_file_content(file1, file2, use_hashing):
    '''same_file_content(file1: filepath, file2: filepath) -> bool

    Checks if `file1` and `file2` have the same content

    Parameters
    ----------
    file1 : filepath
    file2 : filepath
    use_hashing : bool, optional
        if true, hashes the files

    Returns
    -------
    is_same : bool
    '''
    if use_hashing:
        return lazy_hash_file(file1) == lazy_hash_file(file2)
    bufsize = 8192 * 1024
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


_hash_cache = {}
def lazy_hash_file(filename):
    '''
    hash = lazy_hash_file(filename)

    Computes hash for contents of `filename` or look it up in cache
    '''
    if filename not in _hash_cache:
        _hash_cache[filename] = hash_file(filename)
    return _hash_cache[filename]


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
            hash.update(b'link')
            hash.update(readlink(p).encode('utf-8'))
        elif path.isdir(p):
            hash.update(hash_recursive(p))
        elif path.isfile(p):
            hash.update(hash_file(p))
        else:
            raise OSError("Cannot handle files such as `{}`".format(p))
    return hash.hexdigest().encode('ascii')


FileProps = collections.namedtuple('FileProps', ['mode', 'uid', 'gid', 'mtime'])

def props_for(filename, round_secs=False):
    '''
    props = props_for(filename, round_secs=False)

    Properties for `filename`

    round_secs: boolean
        Whether to round mtime to seconds
    '''
    st = os.stat(filename)
    mtime = st.st_mtime
    if round_secs:
        mtime = int(mtime)
    return FileProps(st.st_mode, st.st_uid, st.st_gid, mtime)


class Action(object):
    def __init__(self, f, args):
        self.f = f
        self.args = args

    def run(self):
        self.f(*self.args)


class RemoveAction:
    def __init__(self, f):
        self.f = f

    def run(self):
        os.unlink(self.f)

    def __str__(self):
        return f'RemoveAction({self.f})'


def remove_or_set_oldest(options, ofname, dfname):
    if options.verbose:
        print(f'rm {ofname.decode(errors="ignore")}')
    if options.set_oldest:
        return Action(set_oldest, (ofname,dfname))
    return RemoveAction(ofname)


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
    filequeue = [(b'',sub) for sub in os.scandir(origin)]
    filequeue.sort(key=(lambda sc: sc[1].name), reverse=True)
    while filequeue:
        (basedir, dir_obj) = filequeue.pop()
        ofname = dir_obj.path
        dfname = path.join(dest, basedir, dir_obj.name)
        try:
            if not path.lexists(dfname):
                if not options.remove_only:
                    if options.verbose:
                        print('mv {} {}'.format(ofname, dfname))
                    yield Action(shutil.move, (ofname, dfname))
                elif options.verbose:
                    print('#mv {} {}'.format(ofname, dfname))
            elif dir_obj.is_symlink():
                if not path.islink(dfname):
                    print('File types differ: {}'.format(dir_obj.name))
                elif os.readlink(ofname) == os.readlink(dfname):
                    yield remove_or_set_oldest(options, ofname, dfname)
                else:
                    print('Mismatched link: {}'.format(ofname))
            elif dir_obj.is_dir():
                if options.ignore_git and (dir_obj.name == b'.git' or dir_obj.name.endswith(b'/.git')):
                    print('Skipping .git directory: {}'.format(ofname))
                else:
                    content = sorted([(path.join(basedir, dir_obj.name), subdir) for subdir in os.scandir(ofname)],
                                      key=(lambda sc: sc[1].name),
                                      reverse=True)
                    if options.ignore_git_worktrees and any(subdir.name == b'.git' for _, subdir in content):
                        print('Ignoring .git worktree: {}'.format(ofname))
                    else:
                        for p_s in content:
                            _, s = p_s
                            if options.pre_hash and s.is_file():
                                lazy_hash_file(s.path)
                            filequeue.append(p_s)
            elif not dir_obj.is_file():
                print('Ignoring non-file non-directory: {}'.format(ofname))
            elif not options.ignore_flags and props_for(ofname, options.mtime_ignore_subsec) != props_for(dfname, options.mtime_ignore_subsec):
                if options.verbose:
                    print('Flags differ: {} ({} != {})'.format(dir_obj.name, props_for(dfname, options.mtime_ignore_subsec), props_for(ofname, options.mtime_ignore_subsec)))
                else:
                    print('Flags differ: {}'.format(dir_obj.name))
            elif path.isdir(dfname):
                print('File `{}` matches directory `{}`'.format(ofname, dfname))
            elif not path.isfile(dfname) and not (options.follow_links and path.islink(dfname)):
                print('File `{}` matches non-file `{}`'.format(ofname, dfname))
            elif not same_file_content(ofname, dfname, options.pre_hash):
                print('Content differs: {}'.format(dir_obj.name))
            else:
                yield remove_or_set_oldest(options, ofname, dfname)
        except IOError as e:
            sys.stderr.write('Error accessing `{}`/`{}`: {}\n'.format(ofname, dfname, e))
            if not options.continue_on_error:
                return

def parse_options(argv):
    from optparse import OptionParser
    parser = OptionParser(usage=_usage_simple.format(argv0=argv[0]), version=__version__)
    parser.add_option('--ignore-flags', action='store_true', dest='ignore_flags')
    parser.add_option('--mtime-ignore-subsecond',
                        action='store_true',
                        dest='mtime_ignore_subsec',
                        help='Ignore sub-second difference in mtime')
    parser.add_option('--ignore-git', action='store_true', dest='ignore_git', help='Ignore .git directories')
    parser.add_option('--ignore-git-worktrees', action='store_true', dest='ignore_git_worktrees', help='Ignore git worktree')
    parser.add_option('--remove-only', action='store_true', dest='remove_only', help='Only remove files')
    parser.add_option('--verbose', action='store_true', dest='verbose')
    parser.add_option('--continue-on-error', '--keep-going', action='store_true', dest='continue_on_error', help='Continue on error(s)')
    parser.add_option('--follow-links', action='store_true', dest='follow_links', help='Follow links to content (destination)')
    parser.add_option('--set-oldest', action='store_true', dest='set_oldest', help='Set mtime & atime to oldest of origin/destination')
    parser.add_option('--use-pre-hash', action='store_true', dest='pre_hash',
            help='Use pre-hashing. This is often useful for large files on magnetic disks as it reads the data in a nicer pattern. '
                'However, it requires reading all the input files, so it may result in more IO overall.')
    parser.add_option('--mode',
                        action='store',
                        dest='mode',
                        default='merge',
                        help='What to do [merge/hash]')
    return parser.parse_args(argv)

def main_hashdirs(argv=None):
    if argv is None:
        from sys import argv
        args = argv
    for arg in args[1:]:
        h = hash_recursive(arg)
        print(f'{h.decode("ascii")} {arg}')


def main(argv=None):
    if argv is None:
        from sys import argv
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
        for op in merge(origin.encode('utf-8'), dest.encode('utf-8'), options):
            try:
                op.run()
            except IOError as err:
                sys.stderr.write(f'Error executing {op}: {err}\n')
                if not options.continue_on_error:
                    break
    elif options.mode == 'hash':
        if len(args) < 2:
            from sys import exit
            print('hash mode needs path')
            exit(1)
        for arg in args[1:]:
            h = hash_recursive(arg)
            print('{} {}'.format(h.decode('ascii'), arg))


if __name__ == '__main__':
    main(sys.argv)

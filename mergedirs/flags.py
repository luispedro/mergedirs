def set_oldest(f0, f1):
    '''
    Set mtime and atime for both files to be the oldest of the two.

    Parameters
    ----------
    f0 : str (filepath)
    f1 : str (filepath)
    ''' 
    from os import stat, utime
    s0 = stat(f0)
    s1 = stat(f1)
    if s0.st_atime != s1.st_atime or \
           s0.st_mtime != s1.st_mtime:
        for f in (f0,f1):
            utime(f,
                (min(s0.st_atime, s1.st_atime)
                ,min(s0.st_mtime, s1.st_mtime)))

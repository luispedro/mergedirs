import os
import mergedirs
def test_hash_file():
    h = mergedirs.hash_file('mergedirs/tests/data/A/3')
    h2 = mergedirs.hash_file('mergedirs/tests/data/A/3')
    assert h == h2

def test_props_for():
    p = mergedirs.props_for('mergedirs/tests/data/A/3')
    p2 = mergedirs.props_for('mergedirs/tests/data/A/3')
    assert p == p2
    p2 = mergedirs.props_for('mergedirs/tests/data/B/3')
    assert p != p2

def test_rsync_copy():
    p = mergedirs.props_for('mergedirs/tests/data/A/1')
    p2 = mergedirs.props_for('mergedirs/tests/data/B/1')

    assert p[:3] == p2[:3]
    # Rsync does not always copy the full timestamp, but it should copy the
    # integer version:
    assert int(p[3]) == int(p2[3])

def test_merge():
    options,_ = mergedirs.parse_options(['merge'])
    for op in mergedirs.merge(b'mergedirs/tests/data/A', b'mergedirs/tests/data/B', options):
        assert op.f in (os.rename, os.unlink)

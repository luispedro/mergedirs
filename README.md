# Merge

Merge two directories without losing any content.

It often happens that I have multiple directories that I think are copies of
each other, but don't simply want to erase one of them without checking. This
small utility performs the necessary checks before removing the files.

Usage:

    mergedirs.py INPUT_DIR DEST_DIR

## Flags

- `remove-only`: Do not copy files, only remove duplicates

- `verbose`: be verbose

- `ignore-flags`: ignore file mode, mtime, &c

_AUTHOR_: Luis Pedro Coelho <luis@luispedro.org>

_LICENSE_: MIT


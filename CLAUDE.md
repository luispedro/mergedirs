# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

`mergedirs` merges two directories without losing content: it walks `origin` against `dest`, and for each file that already exists identically at the destination, it removes the origin copy (or moves origin-only files into dest). It errs on the side of doing nothing — any mismatch (different content, mode, mtime, file type, symlink target) is reported and skipped, never overwritten.

## Commands

Install for development:
```bash
pip install -e .
```

Generate test fixtures (required before first test run; the `data/` directory is not checked in):
```bash
cd mergedirs/tests/ && ./gendata.sh && cd ../..
```

Run tests:
```bash
python -m pytest mergedirs/tests/
python -m pytest mergedirs/tests/test_merge.py::test_merge   # single test
```

Entry points (defined in `pyproject.toml`):
- `mergedirs <origin> <dest>` — merge mode (default)
- `mergedirs --mode=hash <dir>...` — recursive directory hash
- `hashdirs <dir>...` — shortcut for hash mode

## Architecture

Two source files matter:

- `mergedirs/merge.py` — all logic. The core is `merge(origin, dest, options)`, a **generator** that yields `Action` objects (`RemoveAction`, `RenameAction`, or wrapped `shutil.move` / `set_oldest`). The caller (`main`) is responsible for iterating and invoking `op.run()`. This separation lets tests inspect the planned actions without touching the filesystem (see `test_merge`).
- `mergedirs/flags.py` — `set_oldest(f0, f1)` normalizes mtime/atime on both files to the older of the pair. Only used when `--set-oldest` is passed (which requires `--ignore-flags`, enforced in `main`).

Key implementation details to preserve when editing:

- Paths flow through `merge` as **bytes**, not str. `main` encodes argv via `.encode('utf-8')` before calling `merge`. Don't decode internally — this is deliberate so non-UTF-8 filenames survive.
- The traversal uses an explicit LIFO `filequeue` of `(basedir, DirEntry)` tuples sorted in reverse so popping yields names in forward order. Don't replace with recursion — large trees rely on this.
- `same_file_content` has two paths: byte-by-byte streaming (default) and `lazy_hash_file` (when `--use-pre-hash` is set). The `_hash_cache` module-global memoizes hashes; pre-hashing is an IO-pattern optimization for spinning disks where reading both files sequentially first beats interleaved reads.
- `--ignore-git` skips `.git` directories entirely. `--ignore-git-worktrees` is different: it skips a directory only if it *contains* a `.git` entry (i.e., the directory is a worktree root), so the worktree itself is preserved while still descending into normal subdirs.
- Property comparison (`props_for`) checks mode/uid/gid/mtime. `--mtime-ignore-subsecond` exists because rsync and some filesystems truncate sub-second precision.

## Notes

- Python 3.10+ (CI matrix: 3.10–3.14).
- Uses `optparse`, not `argparse`.
- `pyproject.toml` reads `__version__` from `mergedirs/mergedirs_version.py`; bump it there.

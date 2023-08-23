import os


def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)  # see below for Python 2.x
        else:
            yield entry


pathlist = ['../../data/training', "../../../SFTP_MA runtime/data",]
           # "/home/max/Desktop/data/"]
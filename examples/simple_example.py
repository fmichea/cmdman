# Example of how a `ls` program could behave.

import cmdman
import os
import sys

def main(args):
    if not os.path.isdir(args.dir):
        raise cmdman.CMDMAN_CMDError('directory does not exist.')
    print('\n'.join(os.listdir(args.dir)))
    return 0

def entry_point():
    with cmdman.cmdman(default_func=main) as c:
        # Add a positional argument for the directory path.
        c.parser.add_argument('dir', action='store',
                              help='relative path to the directory to list.')
        # Parse our arguments and exit on the return code.
        sys.exit(c.parse())

if __name__ == '__main__':
    entry_point()

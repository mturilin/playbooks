#!/usr/bin/env python
from __future__ import print_function
import argparse
import os
import stat
import sys


BASH_START = '#!/bin/bash\n'

def get_lines_or_start_script(fname):
    if os.path.isfile(fname):
        with open(fname) as file:
            print("Opening existing file", fname)
            return file.readlines()
    else:
        print("Creating a new file")
        return [BASH_START]


def writelines(path, lines):
    with open(path, 'w') as file:
        file.write(''.join(lines))
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)


def ensure_bash(lines):
    if lines[0] != BASH_START:
        lines.insert(0, BASH_START)


def main():
    parser = argparse.ArgumentParser(description='Add permanent variable to the virtualenv via postactivate hook')
    parser.add_argument('variables', type=str, nargs='+', help='variable=value')
    args = parser.parse_args()
    pairs = [var.split('=') for var in  args.variables]

    if not hasattr(sys, 'real_prefix'):
        raise RuntimeError("We are not in the virtualenv")


    postactivate_path = sys.prefix + "/bin/postactivate"
    postactivate_lines = get_lines_or_start_script(postactivate_path)

    for key, value in pairs:
        print("Adding", key, end='...')
        export_str = "export %s=%s\n"% (key, value)
        for i in range(0, len(postactivate_lines)):
            if postactivate_lines[i].startswith("export %s="% key):
                if postactivate_lines[i] == export_str:
                    print("ALREADY EXISTS")
                else:
                    postactivate_lines[i] = export_str
                    print("REPLACED")
                break
        else:
            postactivate_lines.append(export_str)
            print("ADDED")

    ensure_bash(postactivate_lines)

    print("Result:")
    for line in postactivate_lines:
        print(line, end='')


    writelines(postactivate_path, postactivate_lines)



if __name__ == "__main__":
    main()
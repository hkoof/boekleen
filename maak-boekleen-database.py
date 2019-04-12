#!/usr/bin/env python3

import sys
import os.path

import boekleenDB

def usage():
    print("""Gebruik:
maak-boekleen-database.py <pad database file>
""", file=sys.stderr)

def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(2)
    filepath = sys.argv[1]
    dirpath = os.path.dirname(filepath)
    if not os.path.isdir(dirpath):
        print("Error: directory {} bestaat niet".format(dirpath), file=sys.stderr)
        sys.exit(1)
    try:
        db = boekleenDB.BoekLeenDB(filepath, create=True)
    except:
        print("Error:", sys.exc_info()[1])
        sys.exit(1)
    print("OK: {} aangemaakt".format(filepath))

if __name__ == "__main__":
    main()


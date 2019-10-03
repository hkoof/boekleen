#!/usr/bin/env python3

import csv as CSV
import sys
import os.path

from boekleenDB import BoekLeenDB

kolommen = [
        'isbn',
        'titel',
        'auteur',
        'omschrijving',
        'trefwoorden',
        'categorie',
        'kastcode',
    ]

def main():
    if len(sys.argv) != 3:
        print("Gebruik: {} <database file> <CSV output file>".format(sys.argv[0]), file=sys.stderr)
        sys.exit(2)
    db = BoekLeenDB(sys.argv[1])
    outputpath = sys.argv[2]
    with open(outputpath, 'x', newline='') as fd:
        boeken = db.alle_boeken_uitgebreid()
        csv = CSV.DictWriter(fd, dialect='excel', fieldnames=kolommen, quoting=CSV.QUOTE_ALL)
        csv.writeheader()
        for boek in boeken:
            dictboek = dict()
            for kol in kolommen:
                dictboek[kol] = boek[kol]
            csv.writerow(dictboek)

if __name__ == "__main__":
    main()


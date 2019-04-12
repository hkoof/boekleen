#!/bin/bash
db=${1:-./test.db}
#./boekleen.py --custom-isbn-prefix=9789020 --database=$db boek kastcode categorie lener uitlenen
./boekleen.py  --database=$db boek kastcode categorie lener uitlenen


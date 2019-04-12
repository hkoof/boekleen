#!/bin/bash
db=${1:-./test.db}
./boekleen.py  --database=$db boek kastcode categorie lener uitlenen


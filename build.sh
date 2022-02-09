#!/usr/bin/bash

pip install pyinstaller

rm -rf dist
pyinstaller rotograph.py

cp installer/install.sh dist/
cp -r assets dist/rotograph/

#!/usr/bin/bash

pip install pyinstaller

pyinstaller rotograph.py

cp installer/install.sh dist/
mkdir dist/desktop
cp installer/rotograph.desktop dist/desktop/
cp -r assets dist/rotograph/

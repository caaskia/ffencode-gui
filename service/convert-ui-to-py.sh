#!/bin/bash

source /home/lynx/pyqt6/pyqt6-env/bin/activate
export LD_LIBRARY_PATH=/home/lynx/pyqt6/pyqt6-env/lib/python3.10/site-packages/PyQt6/Qt6/lib/
sleep 2
# pyqt6-tools designer
cp transcoding_ui.py transcoding_ui.py.bak
pyuic6 transcoding.ui -o transcoding_ui.py

# cd /mnt/data/storeSoft/projPy/ffencode-qt/ffencode_qt/

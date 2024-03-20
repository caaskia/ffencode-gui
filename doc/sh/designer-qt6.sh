#!/bin/bash

cd /home/lynx/pyqt6/
source pyqt6-env/bin/activate
sleep 2
export LD_LIBRARY_PATH=/home/lynx/pyqt6/pyqt6-env/lib/python3.10/site-packages/PyQt6/Qt6/lib/
pyqt6-tools designer


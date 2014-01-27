#!/bin/sh

find ../* -name '__pycache__' -exec rm -r {} +
nosetests --with-coverage
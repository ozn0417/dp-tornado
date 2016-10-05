#!/bin/bash

if [ "$1" = "dry" ]
then
 
  for py_ver in 2.7 3.4; do

    . ./nodeps/$py_ver/bin/activate
    python -m tests
    deactivate
  
  done  

  return
fi

if [ "$1" = "init" ] || [ "$1" = "all" ]
then
  rm -rf builds
  rm -rf dist
  rm -rf dp_tornado.egg-info
  rm -rf nodeps
  virtualenv nodeps/2.7 --python=python2.7
  virtualenv nodeps/3.4 --python=python3.4
fi

for py_ver in 2.7 3.4; do

  . ./nodeps/$py_ver/bin/activate

  if [ "$1" = "install" ] || [ "$1" = "all" ] || [ "$1" = "init" ]
  then
    python setup.py install > /dev/null 2>&1
    pip install nose > /dev/null 2>&1
    pip install CyMySQL==0.8.9

    if [ "$py_ver" = "3.4" ]
    then
      pip uninstall futures -y > /dev/null 2>&1
    fi
  fi

  ./nodeps/$py_ver/bin/nosetests -w ./tests --cover-erase
  deactivate

done

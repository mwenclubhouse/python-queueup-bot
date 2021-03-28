#!/usr/bin/env bash
cd "$(dirname "$0")" || exit
cd ../
git fetch origin
git reset --hard origin/main
python3 setup.py install --user
exit
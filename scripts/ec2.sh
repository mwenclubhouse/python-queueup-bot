#!/usr/bin/env bash
cd "$(dirname "$0")" || exit
cd ../
git fetch origin
git reset --hard origin/main
pip3 uninstall queue_bot -y
python3 setup.py install
cp service/queueup-bot.service /lib/systemd/system 
cp service/queueup-report.service /lib/systemd/system
systemctl daemon-reload
systemctl restart queueup-bot.service
systemctl restart queueup-report.service
loginctl enable-linger $USER
exit

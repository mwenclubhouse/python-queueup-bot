#!/usr/bin/env bash

cd "$(dirname "$0")" || exit
cd ../
mkdir -p ~/.config/systemd/user/
cp service/queueup-bot.service ~/.config/systemd/user/
cp service/queueup-report.service ~/.config/systemd/user/
systemctl daemon-reload --user
systemctl restart queueup-bot.service --user
systemctl restart queueup-report.service --user
loginctl enable-linger $USER
exit

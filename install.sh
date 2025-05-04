#!/usr/bin/env bash

sudo cp fan_controller.py /usr/local/sbin/ && \
sudo cp fan_controller.service /etc/systemd/system/ && \
sudo systemctl stop fan_controller && \
sudo systemctl daemon-reload && \
sudo systemctl start fan_controller

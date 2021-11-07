#!/bin/sh

echo 0 > /sys/class/backlight/soc:backlight/brightness
systemctl stop aplay

#!/bin/sh

echo 1 > /sys/class/backlight/soc:backlight/brightness
systemctl start aplay

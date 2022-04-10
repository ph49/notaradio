# notaradio

## Summary

raspberry pi streaming internet radio
## Hardware 

### Parts list
- raspberry pi zero W
- adafruit [2298](https://www.adafruit.com/product/2298) 320x240 2.8" TFT + Resistive Touchscreen
- adafruit [2465](https://www.adafruit.com/product/2465) powerboost 1000 charger 
- adafruit [3346](https://www.adafruit.com/product/3346) stereo speaker bonnet
- Lithium Ion Battery Pack (e.g. adafruit [354](https://www.adafruit.com/product/354))
- case and speakers from old alarm clock/radio (https://images.app.goo.gl/4F6EjM7qShh4XxYz6)
- slider switch (like adafruit [805](https://www.adafruit.com/product/805))

Hook this all together in the obvious way. 
### Power Switch
The slider switch connects pins GND and EN on the powerboost board, to provide a power on/off switch to the Raspberry Pi.  I soldered a USB micro cable directly to the power output locations on the powerboost board, so this can be attached and detached from the pi zero.

### GPIO pins
The connector to the TFT screen resisted twisting in such a way that I ended up installing the screen upside down (with the micro-switches on the left).

The documentation for the touchscreen says “We bring out GPIO #23, #22, #21, and #18 to the four switch locations!”, but inspection of the schematic indicates that the microswitches are connected to these GPIO pins (listed top-to-bottom with screen to the RIGHT of the microswitches)
|GPIO|
|----|
|BCM 27|
|BCM 23|
|BCM 22|
|BCM 17|

I ended up with this screen configuration in `config.txt` 

```
hdmi_force_hotplug=0
dtparam=spi=on
dtparam=i2c1=on
dtparam=i2c_arm=on
dtoverlay=pitft28-resistive,rotate=90,speed=64000000,fps=30
```

### Backlight:

You can control the screen backlight (on/off) using
```
echo 0 > /sys/class/backlight/soc\:backlight/brightness
```

According to the TFT screen docs, you can set the brightness by using GPIO 18, 
```
gpio -g mode 18 pwm
gpio pwmc 1000
gpio -g pwm 18 100
gpio -g pwm 18 1023
gpio -g pwm 18 0
```

HOWEVER -g 18 is the same as GPIO.1 so it clashes with the sound card, so don’t do that.  Probably should cut this jumper instead.

### Audio Bonnet
The digital audio "bonnet" uses BCM 18, 19, 21

|BCM|GPIO|PHYSICAL|
|-|-|-|
18|GPIO.1|12
19|GPIO.24|35
21|GPIO.29|40


With music playing, you can see these flashing up and down, in `watch -d gpio readall`





## Software Dependencies

## This Code

## WISH LIST / TODO / BUGS

- Bug : kill don't kill the python process, so shutdown don't work

- replace push-button volume control with a rotary encoder
- utilize touch screen
- allow configuration of wifi, station presets, etc without having to extract and edit SD card contents.
- alow configuration via usb micro connector - can the micro connector for charging the powerboost board be split so the data pins go to the non-charging micro connector on the Pi?

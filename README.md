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
- SPST switch (like adafruit [805](https://www.adafruit.com/product/805))
- Rotary Encoder (https://www.adafruit.com/product/377)

Hook this all together in the obvious way. 
### Power Switch
The slider switch connects pins GND and EN on the powerboost board, to provide a power on/off switch to the Raspberry Pi.  Originally I soldered a USB micro cable directly to the power output locations on the powerboost board, so it could be attached and detached from the pi zero's USB power connector.  In later iterations, i power the pi via breakout pins on the audio bonnet, which i attach to breakout pins on the powerboost board.  This seems a bit indirect, but it works better given the physical constraints.

### Screen, and microswitches
The connector to the TFT screen resisted twisting in such a way that I originally ended up installing the screen upside down (with the micro-switches on the left).  In a later remodel, I inverted the pi zero so the ribbon cable no longer has a twist and the screen has the buttons on the right.

I ended up with this screen configuration in `config.txt` 

```
hdmi_force_hotplug=0
dtparam=spi=on
dtparam=i2c1=on
dtparam=i2c_arm=on
dtoverlay=pitft28-resistive,rotate=90,speed=64000000,fps=30
```

The documentation for the touchscreen says “We bring out GPIO #23, #22, #21, and #18 to the four switch locations!”, but inspection of the schematic indicates that the microswitches are connected to these GPIO pins (listed top-to-bottom with screen to the LEFT of the microswitches)
BCM/GPIO|Wiring|Physical|
----|-|-|
17|0|11|
22|3|15|
23|4|16|
27|2|13|


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

HOWEVER -g 18 is the same as GPIO.1 so it clashes with the sound card, so don’t do that.  I cut this trace (https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/backlight-control#:~:text=Disabling%20Backlight%20Control) and now the backlight is on full time.

### Audio Bonnet
The digital audio "bonnet" uses BCM 18, 19, 21

BCM/GPIO|Wiring|PHYSICAL|
-|-|-|
18|1|12|
19|24|35|
21|29|40|


With music playing, you can see these flashing up and down, in `watch -d gpio readall`

### Rotary Encoder
The rotary encoder has 3 connectors: A, B, common. Common is closed with A and B as the spindle is rotated according to this chart
  
    CW ──────►
        ┌─┐ ┌─┐
        │ │ │ │
    A ──┘ └─┘ └─
        ┌─┐ ┌─┐
        │ │ │ │
    B ──┘ └─┘ └─
    ◄──────CCW

Since we're going to know the state at any time, and be detecting transitions, we can write this as a state transition map

A State | B State | Edge | Decoding
--------|---------|--------|----
0|0|A+|CW -> 1,0
0|0|B+|CCW -> 0,1
0|0|A-|XXX 
0|0|B-|XXX
1|0|A+|XXX
1|0|B+|CW -> 1,1
1|0|A-|CCW -> 0,0
1|0|B-|XXX
0|1|A+|CCW -> 1,1
0|1|B+|XXX
0|1|A-|XXX
0|1|B-|CW -> 0,0
1|1|A+|XXX
1|1|B+|XXX
1|1|A-|CW -> 0,1
1|1|B-|CCW -> 1,0

XXX indicates an edge should be ignored - probably too much bounce!

We'll attach A to GPIO5 and to GPIO6


## Software Dependencies

### Python
pip3 install pygame

### Required Packages
apt install libsdl2-2.0-0
apt install libsdl2-ttf-2.0-0
apt install mpg123

### This Code


## WISH LIST / TODO / BUGS

- Bug : kill don't kill the python process, so shutdown don't work

- replace push-button volume control with a rotary encoder.  GPIO pins 

BCM|Wiring|Physical|Notes
-|-|-|-
14||8|
15||10|
18|1|12|used by audio bonnet
23|4|16|used by touchscreen microswitches
24||18|
25||22|
8||24|SPI0 CE0
7||26|SPI0 CE1
1||28|
12||32|
16||36|
20||20|
21|29|40|used by audio bonnet
2||3|
3||5|
4||6|
17|0|11|used by touchscreen microswitches
27|2|13|used by touchscreen microswitches
22|3|15|used by touchscreen microswitches
10||19|SPI0 MOSI
9||21|SPI0 MISO
11||23|SPI0 SCLK
0||27|
5||29|Rotary Encoder A
6||31|Rotary Encoder B
13||33|
19|24|35|used by audio bonnet
26||37|Rotary Encoder Pushbutton




- utilize touch screen
- allow configuration of wifi, station presets, etc without having to extract and edit SD card contents.
- alow configuration via usb micro connector - can the micro connector for charging the powerboost board be split so the data pins go to the non-charging micro connector on the Pi?

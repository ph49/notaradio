import threading
import logging
from pprint import pprint as pp
import RPi.GPIO as GPIO
import time

class Buttons:
    PRESS = 1

    _DEBOUNCE_TIME = 0.15

    GPIO.setmode(GPIO.BCM)
    __bcm = {}

    def set_gpio_handler(bcm, callback, detail=None):
        GPIO.setup(bcm, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(bcm, GPIO.FALLING)
        GPIO.add_event_callback(bcm, Buttons.__detect_edge)
        Buttons.__bcm[bcm] = {
            'bcm': bcm,
            'callback': callback,
            'clicktime': 0,
            'detail': detail
        }

    def __detect_edge(bcm):
        key = Buttons.__bcm[bcm]
        if time.time() - key['clicktime'] < Buttons._DEBOUNCE_TIME:
            return

        key['clicktime'] = time.time()
        key.get('callback', lambda:0)(key['detail'])

    def close():
        print("CLOSE")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    Buttons.set_gpio_handler(17, lambda x: print(x), detail='KEY 0 (BCM=17)')
    Buttons.set_gpio_handler(22, lambda x: print(x), detail='KEY 1 (BCM=22)')
    Buttons.set_gpio_handler(23, lambda x: print(x), detail='KEY 2 (BCM=23)')
    Buttons.set_gpio_handler(27, lambda x: print(x), detail='KEY 3 (BCM=27)')
    print("Press buttons")
    time.sleep(100)

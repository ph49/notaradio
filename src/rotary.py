import threading
import logging
from pprint import pprint as pp
import RPi.GPIO as GPIO
import time

class Rotary:
    PRESS = 1

    _DEBOUNCE_TIME = 0.15

    GPIO.setmode(GPIO.BCM)
    __bcm = {}

    def set_gpio_handler(bcm_a, bcm_b, callback, detail=None):
        GPIO.setup(bcm, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(bcm, GPIO.BOTH)
        GPIO.add_event_callback(bcm, Rotary.__detect_edge)
        Rotary.__bcm[bcm] = {
            'bcm': bcm,
            'callback': callback,
            'detail': detail
        }

    def __detect_edge(bcm):
        key = Rotary.__bcm[bcm]
        if time.time() - key['clicktime'] < Rotary._DEBOUNCE_TIME:
            return

        key['clicktime'] = time.time()
        key.get('callback', lambda:0)(key['detail'])

    def close():
        print("CLOSE")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    Rotary.set_gpio_handler(17, lambda x: print(x), detail='KEY 0 (BCM=17)')
    Rotary.set_gpio_handler(22, lambda x: print(x), detail='KEY 1 (BCM=22)')
    Rotary.set_gpio_handler(23, lambda x: print(x), detail='KEY 2 (BCM=23)')
    Rotary.set_gpio_handler(27, lambda x: print(x), detail='KEY 3 (BCM=27)')
    print("Press Rotary")
    time.sleep(100)

import threading
import logging
from pprint import pprint as pp
import RPi.GPIO as GPIO
import time

class Buttons:
    PRESS = 1

    _DEBOUNCE_TIME = 0.15
    _REPEAT_INTERVAL = .25
    __FIRST_REPEAT_INTERVAL = 0.8

    def __init__(self):
        self.__handlers={}
        GPIO.setmode(GPIO.BCM)
        self.__bcm = {
            27: {'index':0, 'bcm':27, 'callback':lambda key: 0, 'repeat_timer': None, 'repeat_count': 0, 'state':0, 'clicktime': 0},
            23: {'index':1, 'bcm':23, 'callback':lambda key: 0, 'repeat_timer': None, 'repeat_count': 0, 'state':0, 'clicktime': 0},
            22: {'index':2, 'bcm':22, 'callback':lambda key: 0, 'repeat_timer': None, 'repeat_count': 0, 'state':0, 'clicktime': 0},
            17: {'index':3, 'bcm':17, 'callback':lambda key: 0, 'repeat_timer': None, 'repeat_count': 0, 'state':0, 'clicktime': 0}}

        for key in self.__bcm.values():
            GPIO.setup(key['bcm'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(key['bcm'], GPIO.BOTH)
            GPIO.add_event_callback(key['bcm'], self.__detect_edge)

    def __autorepeat(self, bcm):
        key = self.__bcm[bcm]
        if GPIO.input(bcm) == 0: # it is still down
            key['repeat_count'] += 1
            key.get('callback', lambda:0)(key)
            key['repeat_timer'] = threading.Timer(Buttons._REPEAT_INTERVAL, lambda : self.__autorepeat(bcm))
            key['repeat_timer'].start()

    def __detect_edge(self, bcm):
        key = self.__bcm[bcm]
        if time.time() - key['clicktime'] < Buttons._DEBOUNCE_TIME:
            return

        if GPIO.input(key['bcm']) == 0: # it was a button press
            if key['repeat_timer']:
                key['repeat_timer'].cancel()
            key['clicktime'] = time.time()
            key['repeat_count'] = 0
            key.get('callback', lambda:0)(key)
            key['repeat_timer'] = threading.Timer(Buttons.__FIRST_REPEAT_INTERVAL, lambda : self.__autorepeat(bcm))
            key['repeat_timer'].start()
        else: # it was a button release
            if key['repeat_timer']:
                key['repeat_timer'].cancel()

    def set_handler(self, index, callback):
        for key in self.__bcm.values():
            if key['index'] == index:
                key['callback'] = callback

    def close():
        print("CLOSE")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    input = Buttons()
    handle_key = lambda key: pp(key)

    input.set_handler(0, handle_key)        
    input.set_handler(1, handle_key)        
    input.set_handler(2, handle_key)        
    input.set_handler(3, handle_key)        

    print("Press buttons")
    time.sleep(100)

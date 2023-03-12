import threading
import logging
from pprint import pprint as pp
import RPi.GPIO as GPIO
import time

class Rotary:
    __bcm = {}

    # TRANSITIONS [which-gpio][state][which-direction 0/1] = (direction, new-state)
    TRANSITIONS = [
        [ # Edge on GPIO A
            [ # Current state is 0b00
                None, 
                (+1, 0b01)
            ],
            [ # Current state is 0b01 
                (-1, 0b00),
                None
            ],
            [ # Current state is 0b10
                None,
                (-1, 0b11)
            ],
            [ # Current state is 0b11 
                (+1, 0b10),
                None
            ],
        ],
        [ # Edge on GPIO B
            [ # Current state is 0b00
                None, 
                (-1, 0b10)
            ],
            [ # Current state is 0b01 
                None,
                (+1, 0b11)
            ],
            [ # Current state is 0b10
                (+1, 0b00),
                None
            ],
            [ # Current state is 0b11 
                (-1, 0b01),
                None
            ],
        ],
    ]

        

    GPIO.setmode(GPIO.BCM)
    def set_gpio_rotary_handler(bcm_a, bcm_b, callback, detail=None):
        # state is 2-bit encoding of state of bcm_b, bcm_a
        handler = {
            'state' : 0,
            'callback': callback,
            'detail': detail
        }

        for idx, bcm in enumerate([bcm_a, bcm_b]):
            GPIO.setup(bcm, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(bcm, GPIO.BOTH)
            GPIO.add_event_callback(bcm, Rotary.__detect_edge)
            Rotary.__bcm[bcm] = {
                'handler': handler,
                'index': idx,
                'tx': Rotary.TRANSITIONS[idx]
            }


    def __detect_edge(bcm):
        edge = 1 if GPIO.input(bcm) else 0
        key = Rotary.__bcm[bcm]
        state = key['handler']['state']
#        print(f'{bcm} {edge} {state}')
        tx = Rotary.TRANSITIONS[key['index']][state][edge]
        if tx:
#            print(f'{tx[0]} {state}->{tx[1]}')
            key['handler']['state'] = tx[1]    
            key['handler']['callback'](tx[0])
        else:
#            print("XXX")
            pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("Twiddle Knob")
    Rotary.set_gpio_rotary_handler(5, 6, print, detail='Rotary')
    time.sleep(100)

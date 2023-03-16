#!/usr/bin/python3

import logging
import pygame
from pygame import Rect
import os

class Display:
    @classmethod
    def default(cls, *args, **kwargs):
        if os.path.exists("/dev/fb1"):
            return DisplayTft(*args, **kwargs)
        return DisplayDesktop(*args, **kwargs)

    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.__dirty = True
        self.__font = pygame.font.SysFont(None,30)
        self._surface = pygame.Surface((320, 240))
        self.__values = {'volume':0,
            'channel':0,
            'text': ["", "", "", ""]
        }

    def set_volume(self, level):
        self.__values['volume'] = int(level)
        self._dirty()

    def set_channel_text(self, index, text):
        self.__values['text'][index] = text
        self._dirty()

    def set_channel(self, index):
        self.__values['channel'] = index
        self._dirty()

    def _refresh(self):
        raise Exception("ERROR calling _refresh on base class")

    def _dirty(self):
        self.__dirty = True

    def update(self):
        if self.__dirty:
            self.__generate_composed_surface()
            self._refresh()
            self.__dirty = False
        
    def __generate_composed_surface(self):
        # |X1------------------X2-----------------+
        # | |                                     |
        # | |                                     Y1
        # | |                                     |
        # | +-------------------------------------+
        # | |                                     |
        # | |                                     |
        # | |                                     |
        # | +-------------------------------------+
        # | |                                     |
        # | |                                     |
        # | |                                     |
        # | +-------------------------------------+
        # | |                                     |
        # | |                                     |
        # | |                                     |
        # +-+-------------------------------------+

        X1 = 24
        X2 = 320 - X1
        Y1 = 240 / 4
        Y2 = 240
        COL = (80, 80, 200)
        self._surface.fill((0,0,0))
        pygame.draw.rect(self._surface, COL, Rect((0,0),(X1, Y2)),width=2)
        vh = (Y2-8) * (self.__values['volume']/200.0)
        pygame.draw.rect(self._surface, COL, Rect((4,Y2-vh-4),(X1-8, vh)),width=0)
        # pygame.Surface.blit(self._surface, 
        #     self.__font.render("Ch: {}".format(self.__values['channel']), True, (240,240,240)),
        #     (16,self.__layout['Y1']*1/2))
        for ch in range(0,4):
            BG,FG = (0,0,0),(220,220,180) 
            if ch == self.__values['channel']:
                BG,FG = FG,BG
            pygame.draw.rect(self._surface, BG, Rect((X1,Y1*ch),(X2-1, Y1-1)), width=0)
            pygame.Surface.blit(self._surface, 
                self.__font.render(self.__values['text'][ch], True, FG),
                               (X1 + 16, ch*Y1 + Y1/2 - 15))
            pygame.draw.rect(self._surface, COL, Rect((X1,Y1*ch),(X2-1, Y1-1)), width=2)

        # pygame.draw.rect(self._surface, (128,128,128), 
        #     Rect((self.__layout['X1'],240),
        #         (240,240)),
        #     width=2)
        # pygame.Surface.blit(self._surface, 
        #     self.__font.render(self.__values['text'], True, (240,240,240)),
        #         (self.__layout['X1']+8,self.__layout['Y1']))

class DisplayTft(Display):
    def __init__(self, *args, **kwargs):
        import buttons
        import rotary
        super(DisplayTft, self).__init__(*args, **kwargs)

        buttons.Buttons.set_gpio_handler(17, lambda key: pygame.event.post(pygame.event.Event(pygame.KEYDOWN, unicode='1', key=pygame.K_1)))
        buttons.Buttons.set_gpio_handler(22, lambda key: pygame.event.post(pygame.event.Event(pygame.KEYDOWN, unicode='2', key=pygame.K_2)))
        buttons.Buttons.set_gpio_handler(23, lambda key: pygame.event.post(pygame.event.Event(pygame.KEYDOWN, unicode='3', key=pygame.K_3)))
        buttons.Buttons.set_gpio_handler(27, lambda key: pygame.event.post(pygame.event.Event(pygame.KEYDOWN, unicode='4', key=pygame.K_4)))
        buttons.Buttons.set_gpio_handler(26, lambda key: pygame.event.post(pygame.event.Event(pygame.KEYDOWN, unicode=' ', key=pygame.K_SPACE)))
        def level(direction):
            if direction>0:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PLUS, unicode='+'))
            else:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_MINUS, unicode='-'))

        rotary.Rotary.set_gpio_rotary_handler(5, 6, level)

        self.flash_screen()

    def flash_screen(self):
        import time
        self._surface.fill((255,255,255))
        self._refresh()
        time.sleep(0.1)
        self._surface.fill((255,0,0))
        self._refresh()
        time.sleep(0.1)
        self._surface.fill((0,255,0))
        self._refresh()
        time.sleep(0.1)
        self._surface.fill((0,0,255))
        self._refresh()
        time.sleep(0.1)
        self._surface.fill((0,0,0))
        self._refresh()

    def _refresh(self):
        with open("/dev/fb1","wb") as fb:
            fb.write(pygame.transform.rotate(self._surface, 0).convert(16,0).get_buffer())
        # time.sleep(0.1)

class DisplayDesktop(Display):
    def __init__(self, *args, **kwargs):
        super(DisplayDesktop, self).__init__(*args, **kwargs)
        self.__screen = pygame.display.set_mode((320,240))
        pygame.display.set_caption("notaradio")

        self._surface.fill((255,255,255))
        self._refresh()
        self._surface.fill((255,0,0))
        self._refresh()
        self._surface.fill((0,255,0))
        self._refresh()
        self._surface.fill((0,0,255))
        self._refresh()
        self._surface.fill((0,0,0))
        self._refresh()


    def _refresh(self):
        pygame.Surface.blit(self.__screen, self._surface, (0,0))
        pygame.display.update()

if __name__ == "__main__":
    from pprint import pprint as pp
    import time
    import threading

    logging.basicConfig(level=logging.DEBUG)
    display = Display.default()
    display.update()
    ex=[0]
    def end():
        ex[0]=1
        event = pygame.event.Event(pygame.QUIT)
        pygame.event.post(event)

    def vol(n):
        display.set_volume(n)

    def ch(n):
        display.set_channel(n)

    def image(file):
        pass
    

    vol(0)
    ch(1)
    display.set_channel_text(0, "channel 0")
    display.set_channel_text(1, "channel 1")
    display.set_channel_text(2, "channel 2")
    display.set_channel_text(3, "channel 3")
    pygame.time.set_timer(pygame.event.Event(pygame.QUIT), 10000, loops=0)
#    pygame.time.set_timer(pygame.event.Event(pygame.event.custom_type(),name="ev1",callback=lambda: ch(1)), 2000, loops=0)
    pygame.time.set_timer(pygame.event.Event(pygame.event.custom_type(),name="ev2",callback=lambda: ch(1)), 4000, loops=0)
    pygame.time.set_timer(pygame.event.Event(pygame.event.custom_type(),name="ev3",callback=lambda: ch(2)), 6000, loops=0)
    pygame.time.set_timer(pygame.event.Event(pygame.event.custom_type(),name="ev4",callback=lambda: ch(3)), 8000, loops=0)
    while not ex[0]:
        display.update()
        ev = pygame.event.wait()
        print(ev)
        if ev.type == pygame.QUIT:
            os._exit(0)
        else:
            try:
                ev.callback()
            except AttributeError:
                pass


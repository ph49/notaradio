#!/usr/bin/python3

import logging
import pygame
from pygame import Rect
import platform

class Display:
    @classmethod
    def default(cls, *args, **kwargs):
        system = platform.system()
        if system == 'Darwin':
            return DisplayMac(*args, **kwargs)
        elif system == 'Linux':
            return DisplayTft(*args, **kwargs)
        else:
            raise Exception("NO NATIVE DISPLAY")

    def __init__(self):
        self.__volume = 50
        self.__channel = 2
        self.__logo = None
        self.__text = "Ready"
        pygame.init()
        pygame.font.init()
        self.__font = pygame.font.SysFont(None,30)
        self._surface = pygame.Surface((320, 240))
        self.__layout = {
            'X1':320-240,
            'X2':240,
            'Y1':240/2,
            'Y2':64
        }
        self.__values = {'volume':0,
            'channel':0,
            'image':None,
            'text':""}

    def set_volume(self, level):
        self.__values['volume'] = level
        self.update()

    def set_channel(self, level):
        self.__values['channel'] = level
        self.update()

    def set_text(self, text):
        self.__values['text'] = text
        self.update()

    def _refresh(self):
        raise Exception("ERROR calling _refresh on base class")

    def update(self):
        self.__generate_composed_surface()
        self._refresh()
        
    def __generate_composed_surface(self):
        # +-----+--------------------------+
        # |  ^  |                          |
        # Y1 ch |                          |
        # |  v  |       LOGO               |
        # +-X1--+                          |
        # |  ^  |                          |
        # Y1 vol+ - - - - - - - - - - - - -+
        # |  v  |       TEXT               Y2
        # +-----+-------X2-----------------+

        self._surface.fill((0,0,0))
        pygame.draw.rect(self._surface, (128,128,128), 
            Rect((0,0),(self.__layout['X1'],self.__layout['Y1'])),
            width=2)
        pygame.Surface.blit(self._surface, 
            self.__font.render("Ch: {}".format(self.__values['channel']), True, (240,240,240)),
            (16,self.__layout['Y1']*1/2))
        pygame.draw.rect(self._surface, (128,128,128), 
            Rect((0,self.__layout['Y1']),
                (self.__layout['X1'],self.__layout['Y1'])),
            width=2)
        pygame.Surface.blit(self._surface, 
            self.__font.render("Vol: {}".format(self.__values['volume']), True, (240,240,240)),
            (16,self.__layout['Y1']*3/2))
        pygame.draw.rect(self._surface, (128,128,128), 
            Rect((self.__layout['X1'],240),
                (240,240)),
            width=2)
        pygame.Surface.blit(self._surface, 
            self.__font.render(self.__values['text'], True, (240,240,240)),
                (self.__layout['X1']+8,self.__layout['Y1']))

class DisplayTft(Display):
    def __init__(self, *args, **kwargs):
        import buttons
        import time
        super(DisplayTft, self).__init__(*args, **kwargs)
        self._buttons = buttons.Buttons()
        def send_key(keysym):
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=keysym))

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


        self._buttons.set_handler(0, lambda key: send_key(pygame.K_1))
        self._buttons.set_handler(1, lambda key: send_key(pygame.K_2))
        self._buttons.set_handler(2, lambda key: send_key(pygame.K_3))
        self._buttons.set_handler(3, lambda key: send_key(pygame.K_4))

    def _refresh(self):
        with open("/dev/fb1","wb") as fb:
            fb.write(pygame.transform.rotate(self._surface, 180).convert(16,0).get_buffer())
        # time.sleep(0.1)

class DisplayMac(Display):
    def __init__(self, *args, **kwargs):
        super(DisplayMac, self).__init__(*args, **kwargs)
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
    
    def text(str):
        display.set_text(str)

    vol(0)
    ch(1)
    text("")
    threading.Timer(1, lambda: vol(16)).start()
    threading.Timer(2, lambda: ch(2) ).start()
    threading.Timer(3, lambda: text("bananas are yellow")).start()
    threading.Timer(5, end ).start()
    while not ex[0]:
        ev = pygame.event.wait()
        if ev.type == pygame.KEYDOWN:
            pp(ev)

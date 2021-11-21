#!/usr/bin/python3

import logging
import sys
import configparser
import time
import subprocess
from display import Display

from streamplayer import StreamPlayer

class StreamPlayerApp:
    def __init__(self):
        self.config_file = "notaradio.ini"
        self.load_from_config_file()
        self.stream_player = StreamPlayer()
        self.display = Display.default()

        if 'player' in self.config:
            if 'channel' in self.cfg:
                self.select_channel(self.cfg['channel'])
                self.display.set_channel(self.cfg['channel'])
            if 'volume' in self.cfg:
                self.stream_player.set_volume(self.cfg['volume'])
                self.display.set_volume(self.cfg['volume'])
            if 'name' in self.cfg:
                self.display.set_text(self.cfg['name'])

        self.channel = self.select_channel(-1)

    def __del__(self):
        self.stream_player.close()

    def load_from_config_file(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if not 'player' in self.config:
            self.config['player']={}
            with open(self.config_file, "w") as f:
                self.config.write(f)
        self.cfg = self.config['player']

    def select_channel(self, channel):
        channel_id = 'channel {}'.format(channel)
        if channel_id in self.config:
            uri = self.config[channel_id]['uri']
            logging.info("{}: {}".format(channel, uri))
            self.stream_player.select_stream(uri)
            self.display.set_channel(channel)
            self.cfg['channel'] = "{}".format(channel)
            if 'name' in self.config[channel_id]:
                self.cfg['name'] = self.config[channel_id]['name']
                self.display.set_text(self.cfg['name'])
            with open(self.config_file, "w") as f:
                self.config.write(f)        
        return int(self.cfg['channel'])

    def get_volume(self):
        return int(self.cfg.get('volume', '0'))

    def stop(self):
        self.stream_player.stop()

    def change_volume(self, delta):
        volume = self.get_volume()
        volume += delta
        if (volume <0):
            volume = 0
        if (volume >200):
            volume = 200
        self.cfg['volume'] = "{}".format(volume)
        with open(self.config_file, "w") as f:
            self.config.write(f)
        logging.info("VOLUME: {}".format(volume))
        self.stream_player.set_volume(volume)
        self.display.set_volume(volume)
        return volume
       
    def select_stream(self, uri):
        self.cfg['stream'] = "{}".format(uri)
        with open(self.config_file, "w") as f:
            self.config.write(f)
        self.stream_player.select_stream(uri)

    def close(self):
        self.stream_player.close()

    def channel_up(self):
        if not self.awake():
            self.wake_up()
            return
            
        self.channel += 1
        self.channel = self.select_channel(self.channel)

    def channel_down(self):
        if not self.awake():
            self.wake_up()
            return
            
        self.channel -= 1
        self.channel = self.select_channel(self.channel)

    def level_up(self):
        if not self.awake():
            self.wake_up()

        self.change_volume(+5)

    def level_down(self):
        if not self.awake():
            self.wake_up()
            return
            
        if (self.get_volume() == 0):
            self.go_to_sleep()
            return

        self.change_volume(-5)

    def go_to_sleep(self):
        if self.awake():
            self._awake = False
            subprocess.run(["../system/go-to-sleep.sh"])

    def wake_up(self):
        if not self.awake():
            self._awake = True
            subprocess.run(["../system/wake-up.sh"])

    def awake(self):
        return self._awake

    def run(self):
        import pygame
        self._awake = False
        self.wake_up()
        while True:
            ev = pygame.event.wait()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    self.channel_up()
                elif ev.key == pygame.K_2:
                    self.channel_down()
                elif ev.key == pygame.K_3:
                    self.level_up()
                elif ev.key == pygame.K_4:
                    self.level_down()
                else:
                    pass






if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    app = StreamPlayerApp()
    app.run()

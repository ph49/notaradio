#!/usr/bin/python3

import logging
import configparser
import time

from streamplayer import StreamPlayer
from keys import Keys

class StreamPlayerApp:
    def __init__(self):
        self.config_file = "notaradio.ini"
        self.load_from_config_file()
        self.stream_player = StreamPlayer()

        if 'player' in self.config:
            if 'channel' in self.cfg:
                self.select_channel(self.cfg['channel'])
            if 'volume' in self.cfg:
                self.stream_player.set_volume(self.cfg['volume'])

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
            self.stream_player.select_stream(uri)
            self.cfg['channel'] = "{}".format(channel)
            with open(self.config_file, "w") as f:
                self.config.write(f)        
        return int(self.cfg['channel'])

    def change_volume(self, delta):
        volume = int(self.cfg.get('volume', '0'))
        volume += delta
        if (volume <0):
            volume = 0
        if (volume >200):
            volume = 200
        self.cfg['volume'] = "{}".format(volume)
        with open(self.config_file, "w") as f:
            self.config.write(f)
        self.stream_player.set_volume(volume)
        return volume
       
    def select_stream(self, uri):
        self.cfg['stream'] = "{}".format(uri)
        with open(self.config_file, "w") as f:
            self.config.write(f)
        self.stream_player.select_stream(uri)




if __name__ == "__main__":
    from time import sleep
    logging.basicConfig(level=logging.INFO)
    app = StreamPlayerApp()
    keys = Keys()

    channel = [0]
    def channel_up(key):
        channel[0] += 1
        channel[0] = app.select_channel(channel[0])

    def channel_down(key):
        channel[0] -= 1
        channel[0] = app.select_channel(channel[0])

    def level_up(key):
        app.change_volume(+10)

    def level_down(key):
        app.change_volume(-10)

    keys.set_handler(0, channel_up)
    keys.set_handler(1, channel_down)
    keys.set_handler(2, level_up)
    keys.set_handler(3, level_down)

    while True:
        time.sleep(5)
#!/usr/bin/python3

import logging
import configparser
from time import sleep

from streamplayer import StreamPlayer


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
       
    def select_stream(self, uri):
        self.cfg['stream'] = "{}".format(uri)
        with open(self.config_file, "w") as f:
            self.config.write(f)
        self.stream_player.select_stream(uri)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = StreamPlayerApp()
    sleep(4)
    app.select_channel(0)
    sleep(4)
    app.change_volume(-10000)
    app.change_volume(20)
    sleep(2)
    app.change_volume(-10)
    sleep(2)
    app.select_channel(1)
    sleep(4)
    del app

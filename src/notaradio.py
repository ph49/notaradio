#!/usr/bin/python3

import logging
import sys
import configparser
import argparse
import sys
import subprocess
from display import Display

from streamplayer import StreamPlayer

class StreamPlayerApp:
    def __init__(self, argv):
        # defaults
        self.config_file = "notaradio.ini"

        # cli overrides
        self.parse_args(argv)

        # load from file
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

        # read current channel
        self.channel = self.select_channel(-1)

    def __del__(self):
        self.stream_player.close()

    def parse_args(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--configFile')
        args = parser.parse_args(argv)
        if args.configFile:
            self.confconfig_file = args.configFile

    def load_from_config_file(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if not 'player' in self.config:
            self.config['player']={}
            with open(self.config_file, "w") as f:
                self.config.write(f)
        self.cfg = self.config['player']

    def select_channel(self, channel):
        """Select channel, if it's defined

        Args:
            channel (int): Channel number to select. If channel is not defined 
            in the ini file, this channel change will fail

        Returns:
            int: new channel number, or old channel number if no change was made
        """
        
        channel_id = 'channel {}'.format(channel)
        if not channel_id in self.config:
            return int(self.cfg['channel'])
    
        self.cfg['channel'] = "{}".format(channel)
        self.display.set_channel(channel)

        channel_cfg = self.config[channel_id]

        uri = channel_cfg['uri']
        self.stream_player.select_stream(uri)
        self.display.set_text(channel_cfg.get('name', uri))

        with open(self.config_file, "w") as f:
            self.config.write(f)
            
        return channel

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
        self.channel += 1
        self.channel = self.select_channel(self.channel)

    def channel_down(self):
        self.channel -= 1
        self.channel = self.select_channel(self.channel)

    def level_up(self):
        self.change_volume(+5)

    def level_down(self):
        if (self.get_volume() == 0):
            return
        self.change_volume(-5)

    def run(self):
        import pygame

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

    app = StreamPlayerApp(argv=sys.argv[1:])
    app.run()

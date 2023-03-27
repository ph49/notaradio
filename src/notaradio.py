#!/usr/bin/python3

import logging
import sys
import configparser
import argparse
import sys
import subprocess
import os
from display import Display

from streamplayer import StreamPlayer

class NotARadio:
    def __init__(self, argv):
        self.display = Display.default()

        # defaults
        self.config_file = "notaradio.ini"

        # cli overrides
        self.parse_args(argv)

        # load from file
        self.load_from_config_file()
        self.stream_player = StreamPlayer()

        if 'player' in self.config:
            if 'channel' in self.cfg:
                self.select_channel(int(self.cfg['channel']))
                self.display.set_channel(self.cfg['channel'])
            if 'volume' in self.cfg:
                self.stream_player.set_volume(self.cfg['volume'])
                self.display.set_volume(self.cfg['volume'])

    def __del__(self):
        self.stream_player.close()

    def parse_args(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--configFile')
        args = parser.parse_args(argv)
        if args.configFile:
            self.config_file = args.configFile

    def load_from_config_file(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if not 'player' in self.config:
            self.config['player']={}
            self.write_config_file()
        self.cfg = self.config['player']

    def select_channel(self, channel):
        """Select channel, if it's defined

        Args:
            channel (int): Channel number to select. If channel is not defined 
            in the ini file, this channel change will fail

        Returns:
            int: new channel number, or old channel number if no change was made
        """
        
        channel_id = 'channel {}'.format(channel+1)
        if not channel_id in self.config:
            return int(self.cfg['channel'])
    
        self.cfg['channel'] = "{}".format(channel)
        self.display.set_channel(channel)

        channel_cfg = self.config[channel_id]

        uri = channel_cfg['uri']
        self.stream_player.select_stream(uri)
        self.display.set_channel_text(0+channel, channel_cfg.get('name', uri))
        self.write_config_file()
        return channel

    def write_config_file(self):
        with open(self.config_file, "w") as f:
            self.config.write(f)
            f.flush()
            os.fsync(f.fileno())



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
        self.write_config_file()
        logging.info("VOLUME: {}".format(volume))
        self.stream_player.set_volume(volume)
        self.display.set_volume(volume)
        return volume
       
    def select_stream(self, uri):
        self.cfg['stream'] = "{}".format(uri)
        self.write_config_file()
        self.stream_player.select_stream(uri)

    def close(self):
        self.stream_player.close()

    def level_up(self):
        self.change_volume(+5)

    def level_down(self):
        if (self.get_volume() == 0):
            return
        self.change_volume(-5)

    def run(self):
        import pygame

        # Wait for network
        while subprocess.call(['ping', '-c', '1', '8.8.8.8']):
            pass


        ch = self.select_channel(-1)
        self.select_channel(0)
        self.select_channel(1)
        self.select_channel(2)
        self.select_channel(3)
        self.select_channel(ch)
        while True:
            self.display.update()
            ev = pygame.event.wait()
            print(ev)
            if ev.type == pygame.QUIT:
                import os
                self.stop()
                os._exit(0)

            if ev.type == pygame.KEYDOWN:
                code = ev.unicode
                if code == '1':
                    self.select_channel(0)
                elif code == '2':
                    self.select_channel(1)
                elif code == '3':
                    self.select_channel(2)
                elif code == '4':
                    self.select_channel(3)
                elif code == '+':
                    self.level_up()
                elif code == '-':
                    self.level_down()
                elif code == ' ':
                    self.change_volume(-300)
                else:
                    print(ev)






if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    app = NotARadio(argv=sys.argv[1:])
    app.run()

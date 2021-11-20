#!/usr/bin/python3

import logging
import sys
import configparser
import time
import subprocess
from display import Display, DisplayTft

from streamplayer import StreamPlayer
from keys import Keys

class StreamPlayerApp:
    def __init__(self):
        self.config_file = "notaradio.ini"
        self.load_from_config_file()
        self.stream_player = StreamPlayer()
        self.display = DisplayTft()

        if 'player' in self.config:
            if 'channel' in self.cfg:
                self.select_channel(self.cfg['channel'])
                self.display.set_channel(self.cfg['channel'])
            if 'volume' in self.cfg:
                self.stream_player.set_volume(self.cfg['volume'])
                self.display.set_volume(self.cfg['volume'])
            if 'name' in self.cfg:
                self.display.set_text(self.cfg['name'])

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



if __name__ == "__main__":
    from time import sleep
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    app = StreamPlayerApp()
    keys = Keys()
    state = {'app': app}

    channel = [app.select_channel(-1)]

    def getapp():
        return state['app']

    def setapp(app):
        state['app'] = app

    def channel_up(key):
        if not awake():
            wake_up()
            return
            
        channel[0] += 1
        channel[0] = getapp().select_channel(channel[0])

    def channel_down(key):
        if not awake():
            wake_up()
            return
            
        channel[0] -= 1
        channel[0] = getapp().select_channel(channel[0])

    def level_up(key):
        if not awake():
            wake_up()

        getapp().change_volume(+5)

    def level_down(key):
        logging.debug("LEVEL_DOWN")
        if not awake():
            logging.debug("WAKING UP")
            wake_up()
            return
            
        if (getapp().get_volume() == 0):
            logging.debug("GOING TO SLEEP")
            go_to_sleep()
            return

        getapp().change_volume(-5)

    def go_to_sleep():
        if awake():
            state['awake'] = 0
            getapp().close()
            setapp(None)
            subprocess.run(["../system/go-to-sleep.sh"])

    def wake_up():
        if not awake():
            state['awake'] = 1
            subprocess.run(["../system/wake-up.sh"])
            setapp(StreamPlayerApp())
            getapp().change_volume(+5)


    def awake():
        return getapp() != None

    keys.set_handler(0, channel_up)
    keys.set_handler(1, channel_down)
    keys.set_handler(2, level_up)
    keys.set_handler(3, level_down)
    wake_up()

    while True:
        time.sleep(5)
#!/usr/bin/python3

import re
import threading
import logging
import configparser
import subprocess
from pprint import pp
from flask import Flask
from flask_restful import Resource, Api, reqparse
from time import sleep

app = Flask(__name__)
api = Api(app)

class MpgPlayer:
    def load_from_config_file(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        if not 'player' in self.config:
            self.config['player'] = {}
            with open(self.config_file, "w") as f:
                self.config.write(f)
                    
    def __init__(self):
        self.config_file = "notaradio.ini"
        self.load_from_config_file()
        self.start_mpg123()

        if 'player' in self.config:
            if 'stream' in self.config['player']:
                self.select_stream(self.config['player']['stream'])
            if 'volume' in self.config['player']:
                self.set_volume(self.config['player']['volume'])

    def set_volume(self, volume):
        self.config['player']['volume'] = "{}".format(volume)
        with open(self.config_file, "w") as f:
            self.config.write(f)
        self.tell_mpg123("V {}".format(volume))
       
    def select_stream(self, uri):
        self.config['player']['stream'] = "{}".format(uri)
        with open(self.config_file, "w") as f:
            self.config.write(f)
        self.tell_mpg123("L {}".format(uri))

    def mpg123_stdout_reader(self):
        while True:
            a = self.mpg123_popen.stdout.readline()
            logging.debug("{}".format(a))
            if not a:
                break

            match = re.match("^@I ICY-NAME: (.*)", a)
            if match:
                logging.info("ICYNAME: {}".format(match.group(1)))
            
            match = re.match('^@V (\d+)(\.\d+)?', a)
            if match:
                volume = int(match.group(1))
                logging.info("VOLUME: {}".format(volume))

    def start_mpg123(self):
        self.mpg123_popen = subprocess.Popen(["mpg123", "-R"], 
#        self.mpg123_popen = subprocess.Popen(["perl", "foo.pl"], 
            universal_newlines=True,
            bufsize=0, 
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE
            ) 
        self.mpg123_stdout_reader_thread = threading.Thread(target=self.mpg123_stdout_reader)
        self.mpg123_stdout_reader_thread.start()
        self.tell_mpg123("silence")

    def tell_mpg123(self, command):
        self.mpg123_popen.stdin.write("{}\n".format(command))

    def close(self):
        # Terminate (signal 15) does not cause mpg123 -R to exit (on my mac)
        # so try sending SIGINT (which does!)
        self.mpg123_popen.send_signal(2)
        self.mpg123_popen.wait()
        self.mpg123_stdout_reader_thread.join()


logging.basicConfig(level=logging.DEBUG)
if __name__ == "__main__":
    player = MpgPlayer()
    sleep(2)
    player.select_stream("http://ice6.somafm.com/covers-128-mp3")
    sleep(2)
    player.set_volume(100)
    sleep(2)
    player.set_volume(10)
    sleep(2)
    player.select_stream("http://favorites.stream.publicradio.org/favorites.mp3")
    sleep(2)
    player.close()
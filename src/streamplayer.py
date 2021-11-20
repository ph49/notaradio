#!/usr/bin/python3

import re
import threading
import logging
import subprocess

class StreamPlayer:
                    
    def __init__(self):
        self.__start_mpg123()

    def set_volume(self, volume):
        self.__tell_mpg123("V {}".format(volume))
       
    def select_stream(self, uri):
        self.__tell_mpg123("L {}".format(uri))

    def __read_mpg123_stdout(self):
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

    def __start_mpg123(self):
        self.mpg123_popen = subprocess.Popen(["mpg123", "-R"], 
#        self.mpg123_popen = subprocess.Popen(["perl", "foo.pl"], 
            universal_newlines=True,
            bufsize=0, 
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE
            ) 
        self.mpg123_stdout_reader_thread = threading.Thread(target=self.__read_mpg123_stdout)
        self.mpg123_stdout_reader_thread.start()
        self.__tell_mpg123("silence")

    def __tell_mpg123(self, command):
        self.mpg123_popen.stdin.write("{}\n".format(command))

    def stop(self):
        self.__tell_mpg123("s")

    def close(self):
        # Terminate (signal 15) does not cause mpg123 -R to exit (on my mac)
        # so try sending SIGINT (which does!)
        self.mpg123_popen.send_signal(2)
        self.mpg123_popen.wait()
        self.mpg123_stdout_reader_thread.join()


if __name__ == "__main__":
    from time import sleep
    logging.basicConfig(level=logging.DEBUG)
    player = StreamPlayer();
    player.set_volume(10)
    player.select_stream("http://ice6.somafm.com/covers-128-mp3")
    sleep(2)
    player.set_volume(20)
    sleep(2)
    player.select_stream("http://favorites.stream.publicradio.org/favorites.mp3")
    sleep(2)
    player.close()

##########################
#
# Written by Justin Ho
#
##########################

import cv2
import imagezmq
import threading
import copy
from datetime import datetime
from time import sleep

class VideoStreamIngest:
    def __init__(self, port, hostname, opt_reply_msg="SERVER_RECV OK"):
        self.hostname = hostname
        self.port = port
        self.opt_reply_msg = opt_reply_msg.encode()
        self.stop = False
        self.data = None
        self.data_ready = threading.Event()
        self.thread = threading.Thread(target=self._run, args=())
        self.thread.daemon = True
        self.thread.start()

    def receive(self, timeout=None):
        flag = self.data_ready.wait(timeout=timeout)
        if not flag:
            raise TimeoutError("Timeout while reading from video streaming source tcp://{}:{}".format(self.hostname, self.port))
        self.data_ready.clear()
        return self.data

    def _run(self):
        receiver = imagezmq.ImageHub("tcp://{}:{}".format(self.hostname, self.port), REQ_REP=True)
        print("DEBUG: video ingest running...")
        while not self.stop:
            self.data = receiver.recv_jpg()
            receiver.send_reply(self.opt_reply_msg)  # REP reply
            self.data_ready.set()
        receiver.close()

    def close(self):
        print("DEBUG: video ingest exiting...")
        self.stop = True

if __name__ == "__main__":
    pass

    hostname = "[]"             ##change here
    ingest_port = []            ##change here
    receiver = VideoStreamIngest(ingest_port, hostname, opt_reply_msg="SERVER_RECV OK FROM THERMAL NODE")
    sleep(2)
    visualization_on = False

    while True:
        try:
            msg, frame = receiver.receive(timeout=60)
            print(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'), "DEBUG: server received a frame")
        except:
            pass
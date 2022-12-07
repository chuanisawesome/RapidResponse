import cv2
import imagezmq
import threading
import copy
from datetime import datetime

class VideoStreamClientHandle:
    def __init__(self, port, hostname="*"):
        self.hostname = hostname
        self.port = port
        self.video_frame = None
        self.stop = False
        self.lock = threading.Lock()
        self.data_ready = threading.Event()
        self.thread = threading.Thread(target=self._run, args=())
        self.thread.daemon = True
        self.thread.start()
    
    def update_video_frame(self, frame):
        self.lock.acquire()
        self.video_frame = copy.copy(frame)
        self.lock.release()
        self.data_ready.set()


    def _run(self):
        sender = imagezmq.ImageSender("tcp://*:{}".format(self.port), REQ_REP=False)
        print("DEBUG: client handle running...")
        while not self.stop:
            self.data_ready.wait(timeout=None)
            # now we have a new frame
            self.lock.acquire()
            local_video_frame = copy.copy(self.video_frame)
            self.lock.release()
            self.data_ready.clear()
            sender.send_jpg("from dronected server broadcast", local_video_frame)
            print(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'), "DEBUG: server broadcasted a frame")
    
    def close(self):
        print("DEBUG: client handle exiting...")
        self.stop = True

if __name__ == "__main__":
    pass
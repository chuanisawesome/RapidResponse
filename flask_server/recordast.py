import os
import cv2
import numpy as np
import datetime
import time
import threading
import imagezmq

class VideoCamera:

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self._data = None
        self._stop = False
        self._lock = threading.Lock()
        self._data_ready = threading.Event()
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.daemon = True
        self._thread.start()
    
    def _run(self):
        receiver = imagezmq.ImageHub("tcp://{}:{}".format(self.hostname, self.port), REQ_REP=False)
        while not self._stop:
            self._lock.acquire()
            self._data = receiver.recv_jpg()
            self._lock.release()
            self._data_ready.set()
            time.sleep(0.01)
        receiver.close()
    
    def VideoRecord(self):
        self.cam = cv2.VideoCapture(" ") # input link to live video that 
        self.timezone = 0
        # Define the codec
        fourcc = cv2.VideoWriter_fourcc('V','P','8','0')     #using webm codec instead of mp4
        self.out = cv2.VideoWriter('output1.webm', fourcc, 20.0, (int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)),int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        start_time = time.time()
        while(int(time.time() - start_time) < 60):
            ret, frame = self.cam.read()
            if ret==True:
                self.out.write(frame)
            else:
                break
        # where the code is running should be /app
        # Create a black image with same width as main image
        img = np.zeros((50,50,3), np.uint8)
        # Write the date
        font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        bottomLeftCornerOfText = (10,25)
        fontScale = 1
        fontColor = (255,255,255)
        lineType = 1
        # format the datetime
        today = datetime.datetime.now() + datetime.timedelta(hours=self.timezone)
        thedate = '{:%Y/%m/%d %H:%M:%S}'.format(today)
        cv2.putText(img, thedate,
            bottomLeftCornerOfText,
            font,
            fontScale,
            fontColor,
            lineType)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # close camera
        self.cam.release()
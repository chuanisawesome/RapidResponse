from flask import Flask
from flask import Response
import time
import cv2
import numpy as np
import datetime
from VideoStreamClient import VideoStreamIngest

from recordast import VideoCamera

import os
from azure.storage.blob import BlobServiceClient, ContentSettings  ##added contensettings

import threading

# String containing Hostname, Device Id & Device Key in the format:
# "HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>"

# input blob storage keys
storage_account_key = ""
storage_account_name = ""
connection_string = ""
container_name = ""

my_content_settings = ContentSettings(content_type='video/webm')    ##change the content type on blob storage

app = Flask(__name__)

@app.route("/")
def hello_world():
    return """
    <body style="background: black;">
        <div style="width: 1080px; margin: 0px auto;">
            <img src="/mjpeg" width="980" height="661" />
        </div>
    </body>
    """

@app.route("/mjpeg")
def mjpeg():
    return Response(gather_img(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gather_img():
    while True:
        try:
            msg, frame = video.receive(timeout=None)

            if msg:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(0.1)
            else:
                break
        except TimeoutError as e:
            pass


def postblob(file_path,file_name):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    cam.VideoRecord()
    #thread = threading.Thread(target=cam.VideoRecord)
    #thread.start()

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    with open(file_path,"rb") as data:
        blob_client.upload_blob(data, overwrite=True, content_settings=my_content_settings)   ## adding the content type
        print(f"Uploaded {file_name}")
        
@app.route('/recording')
def recording():
    return Response(rec_img(), mimetype='multipart/x-mixed-replace; boundary=frame')

def rec_img():
    while True:
        try:
            msg, frame = video.receive(timeout=None)
            if msg:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(0.1)
            else:
                break
        except TimeoutError as e:
            pass

@app.route('/postimage', methods=['GET'])
def postimage():
    SEGMENT_OUTPUT = "cam1_{timestamp}.webm"
    ts = time.time()
    tsmark = datetime.datetime.fromtimestamp(ts).strftime('%m-%d-%Y_%H-%M')
    vidname = SEGMENT_OUTPUT.replace('{timestamp}', tsmark)
    postblob("output1.webm", vidname)
    return "blob posted"

if __name__ == '__main__':

    publichost = " " # replaced with flask server ip address
    localhost = "127.0.0.1"
    ingest_port= 1234 # replace with port that you want to use
    # record stream
    cam = VideoCamera(ingest_port, publichost)
    # video stream
    video = VideoStreamIngest(ingest_port, publichost, opt_reply_msg="SERVER_RECV OK")
    app.run(host='0.0.0.0', port='443', debug=True, use_reloader=False, threaded=True)
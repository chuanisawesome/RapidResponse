"""
The code is the same as for Tiny Yolo V3 and V4, the only difference is the blob file
- Tiny YOLOv3: https://github.com/david8862/keras-YOLOv3-model-set
- Tiny YOLOv4: https://github.com/TNTWEN/OpenVINO-YOLOV4
"""

import json
import time
from pathlib import Path

import sys
import numpy as np  # numpy - manipulate the packet data returned by depthai
import cv2  # opencv - display the video stream
import depthai as dai # depthai - access the camera and its data packets
import numpy as np
import time

from FramePublisher import FramePublisher

# for Azure IoT Hub
import asyncio
from azure.iot.device import Message
from azure.iot.device.aio import IoTHubDeviceClient


people = 0
banana = 0

cs="" # input IOT Hub connection
CONNECTION_STRING = cs

# PAYLOAD = '{{"peoplecount": {people}, "banana": {banana}}}'
PAYLOAD ={"peoplecount":people, "banana":banana}

# Create pipeline
pipeline = dai.Pipeline()

syncNN = True

# Get argument first
nnPath = str((Path(__file__).parent / Path('../models/yolo-v4-tiny-tf_openvino_2021.4_6shave.blob')).resolve().absolute())
print("Using YoloV4 Model.... Starting now")
if 1 < len(sys.argv):
    arg = sys.argv[1]
    if arg == "yolo3":
        nnPath = str((Path(__file__).parent / Path('../models/yolo-v3-tiny-tf_openvino_2021.4_6shave.blob')).resolve().absolute())
    elif arg == "yolo4":
        nnPath = str((Path(__file__).parent / Path('../models/yolo-v4-tiny-tf_openvino_2021.4_6shave.blob')).resolve().absolute())
    else:
        nnPath = arg
else:
    print("Using Tiny YoloV4 model. If you wish to use Tiny YOLOv3, call 'tiny_yolo.py yolo3'")

if not Path(nnPath).exists():
    import sys
    raise FileNotFoundError(f'Required file/s not found, please run "{sys.executable} install_requirements.py"')

labelMap = "coco.names"
LABELS = open(labelMap).read().strip().split("\n")

# Define sources and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
detectionNetwork = pipeline.create(dai.node.YoloDetectionNetwork)
xoutRgb = pipeline.create(dai.node.XLinkOut)
nnOut = pipeline.create(dai.node.XLinkOut)

xoutRgb.setStreamName("rgb")
nnOut.setStreamName("nn")

# Properties
camRgb.setPreviewSize(416, 416)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
camRgb.setFps(40)

# Network specific settings
detectionNetwork.setConfidenceThreshold(0.5)
detectionNetwork.setNumClasses(80)
detectionNetwork.setCoordinateSize(4)
detectionNetwork.setAnchors([10, 14, 23, 27, 37, 58, 81, 82, 135, 169, 344, 319])
detectionNetwork.setAnchorMasks({"side26": [1, 2, 3], "side13": [3, 4, 5]})
detectionNetwork.setIouThreshold(0.5)
detectionNetwork.setBlobPath(nnPath)
detectionNetwork.setNumInferenceThreads(2)
detectionNetwork.input.setBlocking(False)

# Linking
camRgb.preview.link(detectionNetwork.input)
if syncNN:
    detectionNetwork.passthrough.link(xoutRgb.input)
else:
    camRgb.preview.link(xoutRgb.input)

detectionNetwork.out.link(nnOut.input)


# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    # device.setIrLaserDotProjectorBrightness(100) # in mA, 0..1200
    # device.setIrFloodLightBrightness(0) # in mA, 0..1500
    
    # Output queues will be used to get the rgb frames and nn data from the outputs defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=1, blocking=False)
    qDet = device.getOutputQueue(name="nn", maxSize=1, blocking=False)

    frame = None
    detections = []
    startTime = time.monotonic()
    counter = 0
    color2 = (255, 255, 255)

    # nn data, being the bounding box locations, are in <0..1> range - they need to be normalized with frame width/height
    def frameNorm(frame, bbox):
        normVals = np.full(len(bbox), frame.shape[0])
        normVals[::2] = frame.shape[1]
        return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)\
    
    def displayFrame(name, frame):
        color = (255, 0, 0)
        for detection in detections:
            if LABELS[detection.label] in ['person', 'banana']:
                bbox = frameNorm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
                cv2.putText(frame, LABELS[detection.label], (bbox[0] + 10, bbox[1] + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                cv2.putText(frame, f"{int(detection.confidence * 100)}%", (bbox[0] + 10, bbox[1] + 40), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        # Show the frame
        cv2.imshow(name, frame)


    async def iothub_client_telemetry_run(client):
        print("ast-device sending periodic messages")
        global people
        global banana
        client.connect()

        # detections+=1
        # detections2-=1

        # Build the message with telemetry values.
        person_detect = [det for det in inNN.detections if LABELS[det.label] == 'person']
        people = len(person_detect)

        banana_detections = [det for det in inNN.detections if LABELS[det.label] == 'banana']
        banana = len(banana_detections)
        PAYLOAD["peoplecount"]=people
        PAYLOAD["banana"]=banana

        jsonString = json.dumps(PAYLOAD)
        # print("this is jsonstring" + jsonString)
        message = Message(jsonString)
        
        print("Sending message: {}".format(message))
        await client.send_message(message)
        print ( "Message successfully sent" )
        await asyncio.sleep(0.2 )

    server_address = "" # flask server address
    server_port = "" # flask server

    rpi_opt_message = "sent from camera node"
    frame_publisher = FramePublisher(server_port, server_address, 25, opt_message=rpi_opt_message)

    print("image sent")
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    loop = asyncio.get_event_loop()

    while True:
        inPreview = qRgb.get()
        frame = inPreview.getCvFrame()

        result, frame = cv2.imencode('.jpg', frame, encode_param)         #video encode before sending     
        frame_publisher.publish_uint8_frame(frame)

        inNN = qDet.get()
        detections = inNN.detections
        counter+=1
        current_time = time.monotonic()
        if (current_time - startTime) > 1 :
            fps = counter / (current_time - startTime)
            counter = 0
            startTime = current_time

        # If the frame is available, draw bounding boxes on it and show the frame
        #height = frame.shape[0]
        #width  = frame.shape[1]
        
        #displayFrame("rgb", frame)

        cv2.putText(frame, "NN fps: {:.2f}".format(counter / (time.monotonic() - startTime)),
                            (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color2)
        cv2.putText(frame, f"People count: {people}", (5, 30), cv2.FONT_HERSHEY_TRIPLEX, 1, (0,0,255))

        loop.run_until_complete(iothub_client_telemetry_run(client))
        #imS = cv2.resize(frame, (960, 540))

        #cv2.imshow("frame", frame)

        if cv2.waitKey(1) == ord('q'):
                break

from VideoStreamClientHandle import VideoStreamClientHandle
from VideoStreamIngest import VideoStreamIngest
import cv2
import sys
import copy
import numpy as np
from time import sleep
from datetime import datetime
import traceback

if __name__ == "__main__":
    hostname = ""             ##change to flask server private IP address
    ingest_port = 1234              ##change to a port that is not a common port
    receiver = VideoStreamIngest(ingest_port, hostname, opt_reply_msg="SERVER_RECV OK FROM THERMAL NODE")
    sleep(2)
    client_incoming_port = 41130      ##change here
    clientHandle = VideoStreamClientHandle(client_incoming_port, hostname="*")

    visualization_on = False
    try:
        while True:
            try:
                msg, frame = receiver.receive(timeout=60)
                print(datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'), "DEBUG: server received a frame")
                clientHandle.update_video_frame(frame) # re-distrubute to all client
                image = cv2.imdecode(np.frombuffer(frame, dtype='uint8'), -1)
#                image=jpeg.decode(frame)

                if visualization_on:
                    cv2.imshow("Server received", image)
                    cv2.waitKey(1)
            except TimeoutError as e:
                pass
    except (KeyboardInterrupt, SystemExit):
        print('Exit due to keyboard interrupt')
    except Exception as ex:
        print('Python error with no Exception handler:')
        print('Traceback error:', ex)
        traceback.print_exc()
    finally:
        receiver.close()
        clientHandle.close()
        sys.exit()
import socket
import board
import neopixel 
import time

import requests

# NeoPixels must be connected to D10, D12, D18 or D21 to work on the Raspberry Pi.
# Set to D10 so there will no issue with running on sudo

pixel_pin = board.D10

# The number of NeoPixels
num_pixels = 1

# Choose the order of the pixel colors - RGB or GRB.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)

UDP_IP_ADDR=" " # replace with the static IP that was created from RPi AP
UDP_PORT_NUMBER=8888 # can be replaced with any port that you want to use

serversocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serversocket.bind((UDP_IP_ADDR,UDP_PORT_NUMBER))

print("start")

while True:
    data,address=serversocket.recvfrom(1024)
    print("Message: ", data)
    #simplest way to react.. of course, a better parser should be used, and add GPIO code, etc..
    if data==b'button pressed':
        pixels.fill((255, 0, 0))
        r = requests.get('link to the record session the flask', verify=False, allow_redirects=True)
        pixels.show()
        print("LED ON")
    elif data==b'LED=0\n':
        print("LED OFF")
        # GPIO.output(LED_PIN, GPIO.LOW)

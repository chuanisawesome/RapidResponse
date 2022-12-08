import os
import sys
import time
import subprocess
# USE_LEPTON_35 = True
# USE_CPP_STREAM = True
if __name__ == "__main__":
	time.sleep(5)
	background_proc = []
	
	cam_on= subprocess.Popen("cd /home/pi/Desktop/ast-video/lux/luxcounter; python3 main.py", shell=True, stdout=subprocess.DEVNULL)
	if cam_on.poll() is None:
		print("Camera is turning on...")
		background_proc.append(cam_on)
		time.sleep(1)
	else:
		print("unable to start")
		sys.exit(1)
	
	button_press= subprocess.Popen("cd /home/pi/Desktop; python3 led_udp_test.py", shell=True, stdout=subprocess.DEVNULL)
	if button_press.poll() is None:
		print("button is connected...")
		background_proc.append(button_press)
		time.sleep(2)
	else:
		print("unable to start button connection")
		sys.exit(1)
	
	wg_keep_alive_proc = subprocess.Popen("ping -i 3 8.8.8.8", shell=True, stdout=subprocess.DEVNULL)
	if wg_keep_alive_proc.poll() is None:
		background_proc.append(wg_keep_alive_proc)
		time.sleep(3)
	else:
		print("unable to start")
		sys.exit(1)
	
	print("all subprocess running...")
	exit_codes = [p.wait() for p in background_proc]


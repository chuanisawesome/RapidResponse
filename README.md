# RapidResponse

To ensure that Rapid Reponse work there are two main hardware components that you must have:

- Raspberry Pi 3B+ or higher (for this project we used a Raspberry Pi 4)
- Luxonis usb Camera that can be found [here](https://shop.luxonis.com/collections/usb) (the camera that we used for the project is the Oak-D pro)

Since we are using the Luxonis api there are software dependancy installations that is needed:
[Raspberry Pi OS](https://docs.luxonis.com/projects/api/en/latest/install/?highlight=raspberry%20pi#raspberry-pi-os)
The package can also be installed through PyPI [here](https://docs.luxonis.com/projects/api/en/latest/install/?highlight=raspberry%20pi#install-from-pypi)

## Connection to the Trigger

For the trigger we made the Rasberry Pi a Access Point (AP) the steps that we followed are documented [here](https://thepi.io/how-to-use-your-raspberry-pi-as-a-wireless-access-point/)

To further troubleshoot these were the commands that we ran to ensure that each steps and configurations were properly ran:

`sudo apt install hostapd dnsmasq iptables`
`sudo systemctl stop hostapd`
`sudo systemctl stop dnsmasq`
`sudo nano /etc/dhcpcd.conf`
`sudo systemctl restart dhcpcd`
`systemctl daemon-reload`
`sudo nano /etc/hostapd/hostapd.conf`
`sudo nano /etc/default/hostapd`
`sudo nano /etc/init.d/hostapd`
`sudo nano /etc/dnsmasq.conf`
`sudo nano /etc/sysctl.conf`
`sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"`
`sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE`
`sudo systemctl unmask hostapd`
`sudo systemctl enable hostapd`
`sudo systemctl start hostapd`
`sudo service dnsmasq start`
`systemctl daemon-reload`
`sudo reboot`

## Script for the Trigger

For the Arduino script ensure that the proper library is installed which can be found [here](https://www.arduino.cc/reference/en/libraries/wifi/)

## Startup Script for the Raspberry Pi

The full documentation steps on how to do the startup can be found [here](https://www.pragmaticlinux.com/2020/08/raspberry-pi-startup-script-using-systemd/)

`vi /etc/systemd/system`

[Unit]
Description=Rapid Response Startup Serivce

[Service]
After=network-online.target
Wants=network-online.target
Type=idle
User=pi # change to the user for your raspberry pi
ExecStart=/usr/bin/python3 /home/pi/Desktop/rrl_startup_script.py # change to where the startup script is located
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target

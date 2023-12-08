
# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import serial
import time
import numpy as np


PAGE="""\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

port = serial.Serial("/dev/serial0", baudrate = 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)


while True:
    port.reset_input_buffer()
    print("Starting")
    reading = port.readline()
    print(reading)
    while(reading == b''):
        reading = port.readline()
    rads = []
    print("starting loop:")
    for i in range(0, 179):
        print(f"loop: {i}")
        reading = reading.decode("utf-8")
        value = int(reading.strip())
        rads.append(value)
        reading = port.readline()
    reading = reading.decode("utf-8")
    value = int(reading.strip())
    rads.append(value)
    rads = np.array(rads)
    angles = np.arange(179, -1, -1)
    print(angles)
    print(rads)
    angles = np.pi*angles/180
    file = open('data.csv','w')
    for rad in rads:
        file.write(f"{rads}")
    file.close()




# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming


import time
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.style as mplstyle
import requests


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


fig = plt.figure()
mplstyle.use('fast')
ax = fig.add_subplot(111, projection='polar')


while True:
    rads = []
    url = 'http://10.42.0.1:8000/data.csv'
    r = requests.get(url, allow_redirects=True)
    text = r.text
    text = text.split("\n")
    print(text)
    angles = []
    for t in text:
        if t != '':
            rads.append(int(t))
    angles = np.arange(179, -1, -1)
    print(angles)
    print(rads)
    print(len(rads))
    angles = np.pi*angles/180
    print(angles)
    ax.clear()
    c = ax.plot(angles, rads)
    rads.sort()
    ax.set_ylim([0, rads[-10]])
    plt.savefig("C:\\Users\\danie\\source\\repos\\ControlCenter\\ControlCenter\\plot.png")
    time.sleep(1)

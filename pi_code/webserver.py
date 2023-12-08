# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import serial
import time

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

PAGE2="""\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><img src="plot.png" width="640" height="480"></center>
</body>
</html>
"""
port = serial.Serial("/dev/serial0", baudrate = 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)



class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler, serial.Serial):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path == '/plot.png':
            imgname = self.path
            imgname = imgname[1:]
            imgfile = open(imgname, 'rb').read()
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            self.wfile.write(imgfile)
        elif self.path == '/data.csv':
            filename = self.path
            filename = filename[1:]
            datafile = open(filename, 'rb').read()
            self.send_response(200)
            #self.send_header('Content-type', 'image/png')
            self.end_headers()
            self.wfile.write(datafile)


        elif self.path == '/forward.html':
            self.send_response(200)
            self.end_headers()
            port.write(b'F')
        elif self.path == '/backward.html':
            self.send_response(200)
            self.end_headers()
            port.write(b'B')
        elif self.path == '/left.html':
            self.send_response(200)
            self.end_headers()
            port.write(b'L')
        elif self.path == '/right.html':
            self.send_response(200)
            self.end_headers()
            port.write(b'R')
        elif self.path == '/forward_stop.html':
            self.send_response(200)
            self.end_headers()
            port.write(b'f')
        elif self.path == '/backward_stop.html':
            self.send_response(200)
            self.end_headers()
            port.write(b'b')
        elif self.path == '/left_stop.html':
            self.send_response(200)
            self.end_headers()
            port.write(b'l')
        elif self.path == '/right_stop.html':
            self.send_response(200)
            self.end_headers()
            port.write(b'r')
        elif self.path == '/scan_start.html':
            self.send_response(200)
            self.end_headers()
            port.write(b'S')
        elif self.path == '/scan_stop.html':
            self.send_response(200)
            self.end_headers()
            port.write(b's')
        elif self.path == '/auto.html':
            self.send_response(200)
            self.end_headers()
            port.write(b'A')
        elif self.path == '/manual.html':
            self.send_response(200)
            self.end_headers()
            port.write(b'a')
        elif self.path == '/plot.html':
            content = PAGE2.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)            
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()

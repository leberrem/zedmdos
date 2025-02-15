#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
from urllib.parse import urlparse, parse_qs
import traceback
import datetime
import os
import glob
import json
import re
import random
import multiprocessing

class ZeDMDApiHTTPRequestHandler(BaseHTTPRequestHandler):

    # files_root  = "/usr/share/zedmd-api/www"
    # images_root = "/boot/configs/images"
    # image_logo  = "/usr/share/zedmd-api/logo.png"
    # dmd_play    = "dmd-play"
    # port        = 80

    files_root  = "./www"
    images_root = "../../../../animation"
    image_logo  = "./logo.png"
    dmd_play    = "../../../../dmd-simulator/dmd-play.py"
    port = 9080

    slideshow_thread = None

    def do_GET(self):
        try:
            # api
            if self.path == '/images/list':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                files = glob.glob(ZeDMDApiHTTPRequestHandler.images_root + '/*.gif')
                files.extend(glob.glob(ZeDMDApiHTTPRequestHandler.images_root + '/*.png'))
                for i, f in enumerate(files):
                    files[i] = os.path.basename(f)
                self.wfile.write(json.dumps(files).encode('utf-8'))
                return
            # images
            if self.path.startswith('/images/contents/'):
                imagename = os.path.basename(self.path)
                if ZeDMDApiHTTPRequestHandler.checkfile(imagename):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/octet-stream')
                    self.end_headers()
                    if imagename == "zedmd.png":
                        filename = ZeDMDApiHTTPRequestHandler.image_logo
                    else:
                        filename = ZeDMDApiHTTPRequestHandler.images_root + "/" + imagename
                    with open(filename, 'rb') as fh:
                        self.wfile.write(fh.read())
                else:
                    self.send_response(404)
                    self.end_headers()
                return

            # standard files
            filename = None
            if self.path == '/':
                filename = ZeDMDApiHTTPRequestHandler.files_root + "/index.html"                
            if self.path == '/js/zedmdos-api.js':
                filename = ZeDMDApiHTTPRequestHandler.files_root + self.path
            if filename is not None:
                with open(filename, 'rb') as fh:
                    self.send_response(200)
                    if filename.endswith(".js"):
                        self.send_header('Content-type', 'application/javascript')
                    else:
                        self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    with open(filename, 'rb') as fh:
                        self.wfile.write(fh.read())
            else:
                self.send_response(404)
                self.end_headers()
        except:
            self.send_response(500)
            self.end_headers()
            traceback.print_exc()

    def parameters2rgbargs(p):
        args = [];
        for c in ["r", "g", "b"]:
            if c in p and len(p[c]) == 1:
                args.extend(["-"+c, p[c][0]])
        return args

    def checkfile(f):
        x = re.search("^[0-9a-zA-Z\._-]+$", f)
        return x is not None

    def slideshow(self):
        files = glob.glob(ZeDMDApiHTTPRequestHandler.images_root + '/*.gif')
        while True:
            p = subprocess.Popen([ZeDMDApiHTTPRequestHandler.dmd_play, "--once", "--file", random.choice(files)])
            p.wait()

    def do_POST(self):
        try:
            q = urlparse(self.path)
            p = parse_qs(q.query)

            if ZeDMDApiHTTPRequestHandler.slideshow_thread != None:
                ZeDMDApiHTTPRequestHandler.slideshow_thread.terminate()
                ZeDMDApiHTTPRequestHandler.slideshow_thread = None

            if q.path == "/clock":
                args = [ZeDMDApiHTTPRequestHandler.dmd_play, "--clock"]
                if "format" in p and len(p["format"]) == 1:
                    args.extend(["--clock-format", p["format"][0]])
                args.extend(ZeDMDApiHTTPRequestHandler.parameters2rgbargs(p))
                subprocess.Popen(args)
                self.send_response(200)
                self.end_headers()
            elif q.path == "/countdown":
                countdown = datetime.datetime(datetime.datetime.today().year+1, 1, 1, 0, 0).strftime("%Y-%m-%d %H:%M:%S") # next 1st january
                if "to" in p and len(p["to"]) == 1:
                    countdown = p["to"][0]
                args = [ZeDMDApiHTTPRequestHandler.dmd_play, "--countdown", countdown]
                if "header" in p and len(p["header"]) == 1:
                    args.extend(["--countdown-header", p["header"][0]])
                if "format" in p and len(p["format"]) == 1:
                    args.extend(["--countdown-format", p["format"][0]])
                if "format-0-day" in p and len(p["format-0-day"]) == 1:
                    args.extend(["--countdown-format-0-day", p["format-0-day"][0]])
                if "format-0-hour" in p and len(p["format-0-hour"]) == 1:
                    args.extend(["--countdown-format-0-hour", p["format-0-hour"][0]])
                if "format-0-minute" in p and len(p["format-0-minute"]) == 1:
                    args.extend(["--countdown-format-0-minute", p["format-0-minute"][0]])
                args.extend(ZeDMDApiHTTPRequestHandler.parameters2rgbargs(p))
                subprocess.Popen(args)
                self.send_response(200)
                self.end_headers()
            elif q.path == "/clear":
                subprocess.Popen([ZeDMDApiHTTPRequestHandler.dmd_play, "--clear"])
                self.send_response(200)
                self.end_headers()
            elif q.path == "/text":
                txt = "ZeDMDos"
                if "text" in p and len(p["text"]) == 1:
                    txt = p["text"][0]
                args = [ZeDMDApiHTTPRequestHandler.dmd_play, "--text", txt]
                if "overlay" in p:
                    args.append("--overlay")
                if "overlay-time" in p and len(p["overlay-time"]) == 1:
                    args.extend(["--overlay-time", str(int(p["overlay-time"][0]))])
                if "moving" in p:
                    args.append("--moving-text")
                if "once" in p:
                    args.append("--once")
                if "fixed" in p:
                    args.append("--fixed-text")
                if "ratio" in p:
                    args.append("--no-fit")
                if "align" in p and len(p["align"]) == 1 and p["align"][0] in ["center", "left", "right"]:
                    args.extend(["--align", p["align"][0]])
                args.extend(ZeDMDApiHTTPRequestHandler.parameters2rgbargs(p))
                subprocess.Popen(args)
                self.send_response(200)
                self.end_headers()
            elif q.path == "/image":
                file = None
                if "file" in p and len(p["file"]) == 1:
                    if ZeDMDApiHTTPRequestHandler.checkfile(p["file"][0]):
                        if p["file"][0] == "zedmd.png":
                            file = ZeDMDApiHTTPRequestHandler.image_logo
                        else:
                            file = ZeDMDApiHTTPRequestHandler.images_root + "/" + p["file"][0]
                if file is not None:
                    subprocess.Popen([ZeDMDApiHTTPRequestHandler.dmd_play, "--file", file])
                self.send_response(200)
                self.end_headers()
            elif q.path == "/slideshow":
                ZeDMDApiHTTPRequestHandler.slideshow_thread = multiprocessing.Process(target=self.slideshow)
                ZeDMDApiHTTPRequestHandler.slideshow_thread.start()
                self.send_response(200)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        except:
            self.send_response(500)
            self.end_headers()
            traceback.print_exc()

httpd = HTTPServer(('', ZeDMDApiHTTPRequestHandler.port), ZeDMDApiHTTPRequestHandler)
httpd.serve_forever()

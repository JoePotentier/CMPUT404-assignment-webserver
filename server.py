#!/usr/bin/python3
#  coding: utf-8

# Copyright 2020 Abram Hindle, Eddie Antonio Santos, Joseph Potentier
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import socketserver
import os
import sys
from email.utils import formatdate
from datetime import datetime
from time import mktime


STATIC_FOLDER = os.getcwd() + "/www"


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.response = ""
        self.data = self.request.recv(1024).strip()
        self.method, self.path, self.host = self.get_method_path_host(self.data)
        if self.method != "GET":
            return self.error_handler(405)
        self.path = self.resolve_path(self.path)
        if self.path != None:
            data = self.fetch_file(self.path)
            if data != None:
                self.response += "HTTP/1.1 200 OK\r\n"
                self.determine_mime(self.path)
                self.setContentLen(data)
                self.setServer()
                self.setDateHeader()
                self.response += "Connection: close\r\n"
                self.response += "\r\n"
                self.response += data
                self.request.sendall(self.response.encode("utf-8"))

    def get_method_path_host(self, data):
        data = data.decode("utf-8")
        split_header = data.splitlines()
        split_top = split_header[0].split(" ")
        method = split_top[0]
        path = split_top[1]
        i = 1
        while split_header[i][:5] != "Host:":
            i += 1
        host = split_header[i].split(" ")[1]
        return method, path, host

    def error_handler(self, code):
        if code == 405:
            self.response += "HTTP/1.1 405 Method Not Allowed\r\n"
            self.response += "Allow: GET\r\n"
            self.setServer()
            self.setDateHeader()
            data = self.getErrorPageHtml(405)
            self.setContentLen(data)
            self.response += "Connection: close\r\n"
            self.response += "\r\n"
            self.response += data

        elif code == 301:
            self.response += "HTTP/1.1 301 Moved Permanently\r\n"
            self.response += f"Location: http://{self.host}{self.path}/\r\n"
            self.setServer()
            self.setDateHeader()
            data = self.getErrorPageHtml(301)
            self.setContentLen(data)
            self.response += "Connection: keep-alive\r\n"
            self.response += "\r\n"
            self.response += data
        elif code == 404:
            self.response += "HTTP/1.1 404 Not Found\r\n"
            self.setServer()
            self.setDateHeader()
            data = self.getErrorPageHtml(404)
            self.setContentLen(data)
            self.response += "Connection: close\r\n"
            self.response += "\r\n"
            self.response += data

        self.request.sendall(self.response.encode("utf-8"))

    def resolve_path(self, path):
        if path[-5:] == ".html":
            new_path = STATIC_FOLDER + path
        elif path[-4:] == ".css":
            new_path = STATIC_FOLDER + path
        elif path[len(path) - 1] != "/":
            if os.path.isdir(STATIC_FOLDER + path):
                self.error_handler(301)
            else:
                self.error_handler(404)
            return None
        elif path[len(path) - 1] == "/":
            new_path = STATIC_FOLDER + path + "index.html"
        return new_path

    def fetch_file(self, path):
        try:
            return open(path).read()
        except FileNotFoundError:
            self.error_handler(404)

    def determine_mime(self, path):
        if path[-5:] == ".html":
            self.response += "Content-Type: text/html; charset=UTF-8\r\n"
        elif path[-4:] == ".css":
            self.response += "Content-Type: text/css; charset=UTF-8\r\n"

    def setDateHeader(self):
        # Credit for date formatting: Florian Bösch on StackOverflow - https://stackoverflow.com/a/225106
        now = datetime.now()
        stamp = mktime(now.timetuple())
        self.response += (
            f"Date: {formatdate(timeval=stamp, localtime=False, usegmt=True)}\r\n"
        )

    def setContentLen(self, data):
        length = len(data.encode("utf-8"))
        self.response += f"Content-Length: {length}\r\n"

    def setServer(self):
        self.response += "Server: NOTGODADDY/1.1\r\n"

    def getErrorPageHtml(self, code):
        html = "<!DOCTYPE html><html>"
        if code == 405:
            html += "<head><title>405 Method Not Allowed</title></head>"
            html += "<body><h1>Error: 405 Method Not Allowed</h1><p>We only accept GET requests.</p></body>"
        if code == 301:
            html += "<head><title>301 Moved Permanently</title></head>"
            html += f"<body><h1>Error: 301 Moved Permanently</h1><p>The page you request has moved.</p><p>Location: <a href='http://{self.host}{self.path}/'>http://{self.host}{self.path}/</a></p></body>"
        if code == 404:
            html += "<head><title>404 Not Found</title></head>"
            html += "<body><h1>Error: 404 Not Found</h1><p>The file you requested was not found.</p></body>"
        html += "</html>"
        return html


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

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

STATIC_FOLDER = os.getcwd() + "/www"


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.method, self.path = self.get_method_path_host(self.data)
        if self.method != "GET":
            return self.error_handler(405)
        self.path = self.resolve_path(self.path)
        if self.path != None:
            data = self.fetch_file(self.path)
            if data != None:
                self.request.sendall(b"HTTP/1.1 200 OK\r\n")
                self.request.sendall(b"Connection: close\r\n")
                self.determine_mime(self.path)
                self.request.sendall(b"\r\n")
                self.request.sendall(data.encode())

    def get_method_path_host(self, data):
        data = data.decode("utf-8")
        split_top = data.splitlines()[0].split(" ")
        method = split_top[0]
        path = split_top[1]
        return method, path

    def error_handler(self, code):
        if code == 405:
            self.request.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n")
        elif code == 301:
            self.request.sendall(b"HTTP/1.1 301 Moved Permanently\r\n")
        elif code == 404:
            self.request.sendall(b"HTTP/1.1 404 Not Found\r\n")

    def resolve_path(self, path):
        if path[-5:] == ".html":
            new_path = STATIC_FOLDER + path
        elif path[-4:] == ".css":
            new_path = STATIC_FOLDER + path
        elif path[len(path) - 1] != "/":
            if os.path.isdir(STATIC_FOLDER + path):
                self.error_handler(301)
                corrected_path = f"Location: {self.path}/\r\n"
                self.request.sendall(corrected_path.encode())
                self.request.sendall(b"Connection: keep-alive\r\n")
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
            return self.request.sendall(b"Content-Type: text/html; charset=UTF-8\r\n")
        elif path[-4:] == ".css":
            return self.request.sendall(b"Content-Type: text/css; charset=UTF-8\r\n")


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

#!/usr/bin/python3
#  coding: utf-8

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

import socketserver
import os
import sys

STATIC_FOLDER = os.getcwd() + "/www"

# Partial Credit - sberry on StackOverflow - https://stackoverflow.com/a/18563980
class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.method, self.path, self.host = self.get_method_path_host(self.data)
        if self.method != "GET":
            return self.error_handler(405)
        self.path = self.resolve_path(self.path)
        if self.path != None:
            data = self.fetch_file(self.path)
            if data != None:
                self.request.sendall(b"HTTP/1.1 200 OK\r\n")
                self.determine_mime(self.path)
                self.request.sendall(data.encode())
        self.request.sendall(b"Connection: close\r\n")

    def get_method_path_host(self, data):
        data = data.decode("utf-8")
        split_header = data.splitlines()
        split_top = split_header[0].split(" ")
        method = split_top[0]
        path = split_top[1]
        host = split_header[1].split(" ")[1]
        return method, path, host

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
            self.error_handler(301)
            corrected_path = f"Location: http://{self.host}{self.path}/"
            self.request.sendall(corrected_path.encode("utf-8") + b"\r\n")
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
            return self.request.sendall(b"Content-Type: text/html\r\n")
        elif path[-4:] == ".css":
            return self.request.sendall(b"Content-Type: text/css\r\n")

    # def is_valid_path(self, path, follow_symlinks=True):
    #     # resolves symbolic links
    #     if follow_symlinks:
    #         return os.path.realpath(path).startswith(STATIC_FOLDER)

    #     return os.path.abspath(path).startswith(STATIC_FOLDER)

    # def parse_request(self, req_data):
    #     req_data = req_data.decode("UTF-8")
    #     print(req_data.splitlines())
    #     req_data = req_data.splitlines()
    #     method, path = self.extract_method(req_data[0])
    #     code, file = self.fetch_file(path)
    #     if file is not None:
    #         return 200, file
    #     else:
    #         return code, None

    # def extract_method(self, line_in):
    #     lines = line_in.split(" ")
    #     return lines[0], lines[1]

    # def fetch_file(self, path):
    #     if path == "/":
    #         path = "/index.html"
    #     path = f"./www{path}"
    #     try:
    #         file = open(path)
    #         return 200, file
    #     except FileNotFoundError:
    #         return 404, None

    def is_safe_dir(self, path):
        # https://security.openstack.org/guidelines/dg_using-file-paths.html
        pass


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

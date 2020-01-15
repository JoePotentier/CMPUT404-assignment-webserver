#!/bin/python
#  coding: utf-8
import socketserver

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

# Partial Credit - sberry on StackOverflow - https://stackoverflow.com/a/18563980
class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print("Got a request of: %s\n" % self.data)
        code, file = self.parse_request(self.data)
        if code == 200:
            self.request.sendall(b"HTTP/1.1 200 OK\n")
            self.request.sendall(b"Content-Type: text/html; charset=ISO-8859-4")
            self.request.sendall(file.read().encode())
        else:
            self.request.sendall(b"HTTP/1.1 404 Not Found\n")

    def parse_request(self, req_data):
        req_data = req_data.decode("UTF-8")
        print(req_data.splitlines())
        req_data = req_data.splitlines()
        method, path = self.extract_method(req_data[0])
        code, file = self.fetch_file(path)
        if file is not None:
            return 200, file
        else:
            return code, None

    def extract_method(self, line_in):
        lines = line_in.split(" ")
        return lines[0], lines[1]

    def fetch_file(self, path):
        if path == "/":
            path = "/index.html"
        path = f"./www{path}"
        try:
            file = open(path)
        except FileNotFoundError:
            return 404, None

        return 200, open(path)


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

#  coding: utf-8 
import socketserver
import os

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


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        decoded_data = self.data.decode('utf-8').split('\r\n')
        status_line = decoded_data[0].split(" ")

        if status_line[0] != "GET":
            # Only get methods supported, return 405 error for all other methods
            self.request.sendall(bytearray("HTTP/1.1 405 Method not allowed",'utf-8'))
            return

        requested_file = "www" + status_line[1]
        if os.path.isdir(requested_file):
            if requested_file.endswith("/"):
                # If the request is a directory send the relative index.html
                requested_file += "index.html" 
            else:
                # Use a 301 code to correct the path
                self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\n",'utf-8'))
                self.request.sendall(bytearray("Location: " + status_line[1] + "/",'utf-8'))
                return

        if os.path.isfile(requested_file):
            # Handle the content type
            content_type_line = "Content-Type: "
            if requested_file.endswith(".html"):
                content_type_line += "text/html; charset=utf-8\r\n"
            elif requested_file.endswith(".css"):
                content_type_line += "text/css; charset=utf-8\r\n"

            # Handle the content length
            content_length_line = "Content-Length: " + str(os.path.getsize(requested_file)) + "\r\n"

            # Read the requested file
            file_in = open(requested_file, "rb")
            file_data = file_in.read()
            file_in.close()

            # Send the response header
            self.request.sendall(bytearray("HTTP/1.1 200 OK\r\n",'utf-8'))
            self.request.sendall(bytearray(content_type_line,'utf-8'))
            self.request.sendall(bytearray("Connection: close\r\n",'utf-8'))
            self.request.sendall(bytearray(content_length_line,'utf-8'))

            # Send the response body
            self.request.sendall(bytearray("\r\n",'utf-8'))
            self.request.sendall(file_data)
        else:
            # The requested file was not found, so send a 404 error
            self.request.sendall(bytearray("HTTP/1.1 404 Not found",'utf-8'))
            return


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

#!/usr/bin/env python
from http import server
import socket
import tqdm
import os
import json
import dbFunction as db
from http.server import BaseHTTPRequestHandler, HTTPServer


# device's IP address
SERVER_HOST = "192.168.0.34"
SERVER_PORT = 9000
# receive 4096 bytes each time
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"


def write_json(new_sensor, ID, filename='/home/ale/spectrum-analyzer/src/data/data.json'):
    with open(filename, 'r+') as f:
        data = json.load(f)
        data[ID] = new_sensor
        f.seek(0)
        json.dump(data, f, indent=4)


# create the server socket
# TCP socket
s = socket.socket()
# bind the socket to our local address
s.bind((SERVER_HOST, SERVER_PORT))
# enabling our server to accept connections
# 5 here is the number of unaccepted connections that
# the system will allow before refusing new connections
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
while True:
    # accept connection if there is any
    client_socket, address = s.accept()
    # if below code is executed, that means the sender is connected
    print(f"[+] {address} is connected")
    # receive the file infos
    # receive using client socket, not server socket
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize, sensor_name, location, latitude, longitude, isnew = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)
    # start receiving the file from the socket
    # and writing to the file stream
    #progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            #progress.update(len(bytes_read))
        print(f"[+] {address} File '{filename}' received successfully")
    if isnew == "True":
        new_sensor = {
            'name': sensor_name,
            'location': location,
            'latitude': latitude,
            'longitude': longitude
        }
        write_json(new_sensor, sensor_name+location)
        db.insert_data(sensor_name+location, filename)
    else:
        db.update_data(sensor_name+location, filename)

    #close the client socket
    #client_socket.close()
    #close the server socket
    #s.close()

    

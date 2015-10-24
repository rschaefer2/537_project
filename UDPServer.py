__author__ = 'bvschaefer'

import socket
import sys
import ast
import select
import pickle

class FrameResp:
    frame_number = 0
    movie_title = ""
    ba = b'\x00' * 1024

    def __init__(self, frame_number, movie_title, data):
        self.frame_number = frame_number
        self.movie_title = movie_title
        self.ba = data

UDP_PORT = int(sys.argv[1])

server_address = (socket.gethostname(), UDP_PORT)

# create socket and bind to port on localmachine
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(server_address)

# create an empty dictionary to save received data
data_dict = {}
# socket_list must be a sequence
socket_list = [sock]

while True:
    # check if req from client is pending
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [], 0)

    for s in read_sockets:
        if s == sock:
            recv_size = 40
            data = 0
            data, address = s.recvfrom(recv_size)
            recv_size -= len(data)
            while (recv_size != 0):
                print("Didnt receive full Frame")
                temp_data, address = s.recvfrom(recv_size)
                recv_size -= len(data)
                data += temp_data

            # check if data is valid
            if not data:
                    sys.stdout.write('\nDisconnected from server')
            else :
                # save data received in string
                # send response if valid data
                with open(data[5:].split(b'\0', 1)[0]) as fin:
                    fin.seek(int(data[:5].split(b'\0', 1)[0]) * 1024)
                    send_data = fin.read(1024)
                    barray = bytearray()
                    barray.extend(data[:5])
                    barray.extend(send_data)

                    # send response
                    s.sendto(barray, address)
                    print(barray)




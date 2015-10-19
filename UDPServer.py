__author__ = 'bvschaefer'

import socket
import sys
import random
import select
import pickle

class FrameReq:
    frame_number = 0
    movie_title = ""

    def __init__(self, frame_number, movie_title):
        self.frame_number = frame_number
        self.movie_title = movie_title

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
# data_dict = {}
# socket_list must be a sequence
socket_list = [sock]

while True:
    # check if req from client is pending
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

    for s in read_sockets:
        if s == sock:
            data, address = s.recvfrom(FrameReq.__sizeof__())
            # check if data is valid
            if not data:
                    sys.stdout.write('\nDisconnected from server')
            else :
                # deserialize request from client
                frame_request = pickle.load(data)

                # print data for now
                sys.stdout.write(frame_request.movie_title)
                sys.stdout.write(frame_request.frame_number)

                with open(frame_request.movie_title) as fin:
                    fin.seek(frame_request.frame_number * 1024)
                    data = fin.read(1024)
                    send_frame = FrameResp(frame_request.frame_number, frame_request.movie_title, data)

                    # send response
                    s.sendto(pickle.dumps(send_frame), address)
    break




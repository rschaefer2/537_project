import socket
import select
import sys
from MovieClient import Frame
import datetime

global data
currentFrame = 0
UDP_IP = sys.argv[1]
UDP_PORT = sys.argv[2]
server = (UDP_IP, UDP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_list = [sock]
try:
    movie = sys.argv[3]
except IndexError:
    movie = "Happy Gilmore wasn't such a good man he was a stupid man and had a lot of problems"


def create_request_array(frame_number, movie_title):
    barr = bytearray()
    barr.extend("{}".format(frame_number))
    barr.extend(bytearray(5-len(barr)))
    barr.extend(movie_title)
    if len(barr) > 40:
        barr = barr[:40]
    else:
        barr.extend(bytearray(40-len(barr)))
    return barr


def receive_data():
    """receives data from the socket. Returns a Frame if enough data, else returns none"""
    global data
    bytes_received = len(data)
    data += sock.recvfrom(1029-bytes_received)
    if len(data) is 1049:
        frame_number = int(data[:5])
        frame_data = data[6:]
        frame = Frame(frame_number, data)
        data = ""
        return frame
    else:
        return None


message = create_request_array(currentFrame, movie)
sock.sendto(message, server)
while currentFrame <= 30000:
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    for s in read_sockets:
        if s == sock:
            frame = receive_data()
            if frame:
                # add frame to buffer
                currentFrame += 1
            else:
                pass








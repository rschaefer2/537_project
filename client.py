import socket
import select
import sys
from MovieClient import Frame, FrameBuffer
import time


current_milli_time = lambda: int(round(time.time() * 1000))

data = ''
currentFrame = 0
UDP_IP = sys.argv[1]
UDP_PORT = int(sys.argv[2])
server = (UDP_IP, UDP_PORT)
frame_buffer = FrameBuffer(31)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_list = [sock]
try:
    movie = sys.argv[3]
except IndexError:
    movie = "test_movie.txt"


def frame_request_list(buf):
    diff = buf.firstFrameIndex - buf.currentIndex
    if diff < 0:
        diff += 32
    if diff < 2:
        start = buf.framebuf[buf.firstFrameIndex].frame_num
        if start < 0:
            start = 0
        return range(start, 16-diff)
    else:
        return []


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
    print("Receiving Data")
    bytes_received = len(data)
    data += sock.recvfrom(1029-bytes_received)[0]
    print(len(data))
    print(data)
    if len(data) >= 1029:
        frame_number = int(data[:5].split(b'\0', 1)[0])
        frame_data = data[6:1029].split(b'\0', 1)[0]
        frame = Frame(frame_number, data)
        if len(data) > 1029:
            data = data[1030:]
        else:
            data = ""
        frame_buffer.addFrame(frame)
        return frame
    else:
        return None

message = create_request_array(currentFrame, movie)
sock.sendto(message, server)
last_frame = current_milli_time()
print(last_frame)
while currentFrame <= 10:

#read data if its available
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [], 0)
    for s in read_sockets:
        if s == sock:
            frame = receive_data()


#print next frame if its > 10ms
    diff = current_milli_time() - last_frame
    if diff >= 10:
        frame = frame_buffer.next_frame()
        if frame:
            print(str(frame.frame_num) + frame.data)
            print("Time: {}".format(diff))
            last_frame = current_milli_time()
            message = create_request_array(frame.frame_num + 1, movie)
            sock.sendto(message, server)
            currentFrame += 1

        else:
            pass

        frame_list = frame_request_list(frame_buffer)
        for i in frame_list:
                print(i)
                message = create_request_array(i, movie)
                sock.sendto(message,server)
"""
#request front of buffer frame if currentindex is too close
    frame_list = frame_request_list(frame_buffer)
    for i in frame_list:
            print(i)
            message = create_request_array(i, movie)
            sock.sendto(message,server)
"""







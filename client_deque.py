import socket
import select
import sys
from MovieClient import Frame, FrameBuffer
import time
import collections


def add_to_deque(deque, flist, last_frame_num, request_list):
    try:
        new_num = deque[0].frame_num + 1
    except IndexError:
        new_num = last_frame_num + 1
        print("Index Error, Frame")
    if new_num < 30000:
        for i in range(len(flist)):
            if flist[i].frame_num == new_num:
                deque.appendleft(flist.pop(i))
                print("Found Frame in List!")
                return
        print("Frame {} not in list, send request to server?".format(new_num))
        if new_num not in request_list:
            mess = create_request_array(new_num, movie)
            sock.sendto(mess, server)
            request_list.appendleft(new_num)


def add_frame_to_list(frame_list, new_frame, last_frame_num):
    new_num = new_frame.frame_num
    # only add the frame if its greater than the most forward frame
    try:
        front_num = frame_deque[0].frame_num
    except IndexError:
        front_num = last_frame_num
    if new_num > front_num:
        # only add frame if the list isn't "full"
        if len(frame_list) < 4:
            # only add frame if the frame isn't already in the list
            if new_num not in [x.frame_num for x in frame_list]:
                frame_list.append(new_frame)
                print("Added Frame {} to buffer".format(new_num))
            else:
                print("Frame {} Dropped: Frame Already in Buffer".format(new_num))
        else:
            print("Frame {} Dropped: Frame List Full".format(new_num))
    else:
        print("Frame {} Dropped: Behind furthest frame Number".format(new_num))
        print("furthest frame: {}".format(front_num))


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


def receive_data(frame_list, last_frame_num):
    """receives data from the socket. Returns a Frame if enough data, else returns none"""
    global data
    bytes_received = len(data)
    data += sock.recvfrom(1029-bytes_received)[0]
    if len(data) >= 1029:
        frame_number = int(data[:5].split(b'\0', 1)[0])
        frame_data = data[6:1029].split(b'\0', 1)[0]
        new_frame = Frame(frame_number, data)
        if len(data) > 1029:
            data = data[1030:]
        else:
            data = ""
        print("Receiving Frame {}".format(frame_number))
        add_frame_to_list(frame_list, new_frame, last_frame_num)



def current_milli_time():
    return int(round(time.time() * 1000))


data = ''
UDP_IP = sys.argv[1]
UDP_PORT = int(sys.argv[2])
server = (UDP_IP, UDP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_list = [sock]
try:
    movie = sys.argv[3]
except IndexError:
    movie = "test_movie.txt"

currentFrame = 0
frame_deque = collections.deque(maxlen=28)
frame_list = []
frame_times = []
requests_sent = collections.deque()
last_frame_num = -1


message = create_request_array(currentFrame, movie)
sock.sendto(message, server)
last_frame = current_milli_time()
# main loop
while currentFrame <= 300:

    # read data if its available
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [], 0)
    for s in read_sockets:
        if s == sock:
            receive_data(frame_list, last_frame_num)

    # print next frame if its > 10ms
    diff = current_milli_time() - last_frame
    if diff >= 10:
        try:
            frame = frame_deque.pop()
            if len(frame_deque) == 0:
                last_frame_num = frame.frame_num
        except IndexError:
            frame = None
        if frame:
            print("Time: {}".format(diff))
            frame_times.append(diff)
            last_frame = current_milli_time()
            currentFrame = frame.frame_num + 1

    # check if deque needs to be filled
    if len(frame_deque) != frame_deque.maxlen:
        add_to_deque(frame_deque, frame_list, last_frame_num, requests_sent)

print(frame_times)

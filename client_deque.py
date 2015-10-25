import socket
import select
import sys
from MovieClient import Frame, FrameBuffer
import time
import collections



server_list = [9876, 9877, 9878, 9879]
server_index = 0

# adds one frame from the list to the deque. plenty fast enough
def add_to_deque(deque, flist, last_frame_num, request_list):
    try:
        new_num = deque[0].frame_num + 1
    except IndexError:
        new_num = last_frame_num + 1
        print("!!! Deque Empty !!!")
    if new_num < 30000:
        for i in range(len(flist)):
            if flist[i].frame_num == new_num:
                deque.appendleft(flist.pop(i))
                #print("Found Frame in List!")
                return
        print("Deque not full: Frame {} not in list".format(new_num))

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

def fill_list(frame_deque, frame_list, last_frame_num, request_list):
    # sends requests for the empty spots in the list
    empty = 4 - len(frame_list)
    try:
        next_num = frame_deque[0].frame_num + 1
    except IndexError:
        next_num = last_frame_num + 1
    while empty > 0:
        if next_num in [x.frame_num for x in frame_list]:
            next_num += 1
        elif next_num in requests_sent:
            next_num += 1
            empty -= 1
        else:
            print("Filling List: Send Request for {}".format(next_num))
            message = create_request_array(next_num, movie)
            sock.sendto(message, server)
            request_list.appendleft(next_num)
            next_num += 1
            empty -= 1


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

# initialize frame deque (buffer)
#while len(frame_deque) != frame_deque.maxlen:




message = create_request_array(currentFrame, movie)
sock.sendto(message, server)
last_frame = current_milli_time()
# main loop
while currentFrame <= 10000:

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
            frame_times.append(diff)
            last_frame = current_milli_time()
            currentFrame = frame.frame_num + 1

    # request more than one frame in a row
    fill_list(frame_deque, frame_list, last_frame_num, requests_sent)

    # check if deque needs to be filled
    if len(frame_deque) != frame_deque.maxlen:
        add_to_deque(frame_deque, frame_list, last_frame_num, requests_sent)

print(frame_times)

print sum(frame_times)/ float(len(frame_times))

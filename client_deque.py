import socket
import select
import sys
from MovieClient import Frame, FrameBuffer
import time
import collections
import threading
from qos import QoS

server_list = [9876, 9877, 9878, 9879]
server_index = 0
TIMEOUT = 900


def add_to_deque(deque, flist, last_frame_num, request_list):
    try:
        new_num = deque[0].frame_num + 1
    except IndexError:
        new_num = last_frame_num + 1
        # print("!!! Deque Empty !!!")
    if new_num <= 30000:
        for i,f in enumerate(flist):
            if f.frame_num == new_num:
                deque.appendleft(flist.pop(i))
                # print("Deque not full: Frame {} not in list".format(new_num))


def add_frame_to_list(frame_list, new_frame, last_frame_num):
    new_num = new_frame.frame_num
    # only add the frame if its greater than the most forward frame
    try:
        front_num = frame_deque[0].frame_num
    except IndexError:
        front_num = last_frame_num
    if new_num > front_num:
        # only add frame if the list isn't "full"
        if len(frame_list) < frame_list_max:
            # only add frame if the frame isn't already in the list
            if new_num not in [x.frame_num for x in frame_list]:
                frame_list.append(new_frame)
                #print("Added Frame {} to buffer".format(new_num))
            #else:
                #print("Frame {} Dropped: Frame Already in Buffer".format(new_num))
        else:
            print("Frame {} Dropped: Frame List Full".format(new_num))
    else:
        print("Frame {} Dropped: Behind furthest frame Number".format(new_num))
    print "Out of order length: {}".format(len(frame_list))
    print [x.frame_num for x in frame_list]
    print front_num


def fill_list(frame_deque, frame_list, last_frame_num, request_list):
    # sends requests for the empty spots in the list
    empty = frame_list_max - len(frame_list) + 1
    try:
        next_num = frame_deque[0].frame_num + 1
    except IndexError:
        next_num = last_frame_num + 1
    while empty > 0:
        if next_num in [x.frame_num for x in frame_list]:
            # print("Frame {} already received".format(next_num))
            next_num += 1
        elif next_num in [x[0] for x in request_list]:
            for index_req, request in enumerate(request_list):
                if request[0] == next_num:
                    # print("frame {} already requested".format(request))
                    # print("current_time - time_sent = {}".format(current_milli_time() - request[1]))
                    if current_milli_time() - request[1] > TIMEOUT:
                        print("!!!TIMEOUT!!!")
                        for index, server in enumerate(active_server_list):
                            if request[2] == server[0]:
                                #print("server {}".format(x[2]))
                                del (active_server_list[index])
                        print("Filling List: Send Request for {}".format(next_num))
                        print("{}".format(active_server_list))
                        if len(active_server_list) == 0:
                            print("Active list is empty")
                            return
                        message = create_request_array(next_num, movie)
                        server = active_server_list[next_num % len(active_server_list)][0]
                        socket = active_server_list[next_num % len(active_server_list)][1]
                        socket.sendto(message,server)
                        request_list[index_req] = ((next_num, current_milli_time(), server))
            next_num += 1
            empty -= 1
        else:
            if next_num > 30000:
                return
            #print("Filling List: Send Request for {}".format(next_num))
            message = create_request_array(next_num, movie)
            server = active_server_list[next_num % len(active_server_list)][0]
            socket = active_server_list[next_num % len(active_server_list)][1]
            socket.sendto(message,server)
            """if next_num % 4 == 0:
                sock1.sendto(message, server1)
            if next_num % 4 == 1:
                sock2.sendto(message, server2)
            if next_num % 4 == 2:
                sock3.sendto(message, server3)
            if next_num % 4 == 3:
                sock4.sendto(message, server4)
            """
            request_list.appendleft((next_num, current_milli_time(), server))
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


def receive_data(frame_list, last_frame_num, socket):
    """receives data from the socket. Returns a Frame if enough data, else returns none"""
    global data, inorder, ooorder
    bytes_received = len(data)
    data += socket.recvfrom(1029-bytes_received)[0]
    if len(data) >= 1029:
        frame_number = int(data[:5].split(b'\0', 1)[0])
        frame_data = data[6:1029].split(b'\0', 1)[0]
        new_frame = Frame(frame_number, data)
        if frame_number == 9999:
            print("!!!!----------Client received qos packet---------!!!!")
            return
        if len(data) > 1029:
            data = data[1030:]
        else:
            data = ""

    try:
        frame_num = frame_deque[0].frame_num
    except:
        frame_num = last_frame_num

    if new_frame.frame_num == frame_num + 1 and len(frame_deque) != frame_deque.maxlen:
        print "!!STRAIGHT TO DEQUE!! {}".format(new_frame.frame_num)
        inorder += 1
        frame_deque.appendleft(new_frame)
    else:
        ooorder += 1
        add_frame_to_list(frame_list, new_frame, last_frame_num)

    # find frame in request_list and remove it
    for i, x in enumerate(requests_sent):
        if x[0] == frame_number:
            RTT.append(current_milli_time() - x[1])
            del requests_sent[i]
        print("request_list: {}".format([(x[0], current_milli_time() - x[1]) for x in requests_sent]))
        return

def command_control(commands, stop_event):
    while not stop_event.is_set():
        print "Command Control\n"
        command = raw_input("Please enter a command: ")
        commands.append(command)

        if command.startswith("q"):
            break

def pause(commands):
    while 1:
        read_sockets, write_sockets, error_sockets = select.select([x[1] for x in active_server_list], [], [], 0)
        for s in read_sockets:
            if s == sock1 or s == sock2 or s == sock3 or s == sock4:
                receive_data(frame_list, last_frame_num, s)
        try:
            command = commands.pop()
        except IndexError:
            command = None
        if command and command.startswith("p"):
            last_frame = current_milli_time()
            return


def process_commands(commands):
    global last_frame_num
    global last_frame
    try:
        command = commands.pop()
    except IndexError:
        return

    if command:
        if command.startswith("p"):
            pause(commands)
        else:
            command = command.split(" ")
            if command[0].startswith("f"):
                currentFrame = int(command[1])
                frame_deque.clear()
                del frame_list[:]
                requests_sent.clear()
                last_frame_num = currentFrame - 1
            elif command[0].startswith("r"):
                currentFrame = int(command[1])
                frame_deque.clear()
                frame_list.clear()
                requests_sent.clear()
                last_frame_num = currentFrame - 1
            elif command[0].startswith("q"):
                sys.exit("Exiting...")
        buffering()
        last_frame = current_milli_time()

def current_milli_time():
    return int(round(time.time() * 1000))


inorder = 0
ooorder = 0
data = ''

UDP_IP = sys.argv[1]
UDP_PORT = int(sys.argv[2])
server1 = (UDP_IP, UDP_PORT)

UDP_IP = sys.argv[3]
UDP_PORT = int(sys.argv[4])
server2 = (UDP_IP, UDP_PORT)

UDP_IP = sys.argv[5]
UDP_PORT = int(sys.argv[6])
server3 = (UDP_IP, UDP_PORT)

UDP_IP = sys.argv[7]
UDP_PORT = int(sys.argv[8])
server4 = (UDP_IP, UDP_PORT)

sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

active_list_lock = threading.Lock()
global_server_list = [(server1, sock1), (server2, sock2), (server3, sock3), (server4, sock4)]
active_server_list = [(server1, sock1), (server2, sock2), (server3, sock3), (server4, sock4)]


# Start Qos thread
# task = QoS.start()

print("Qos Start")
# QoS(active_list_lock, global_server_list, active_server_list)
t = threading.Thread(target=QoS, args=(active_list_lock, global_server_list, active_server_list))
t.start()
print("Qos back round")

# start user input processing thread
commands = collections.deque()
control_stop = threading.Event()
control = threading.Thread(None, command_control, None, (commands,control_stop), {})
control.start()

try:
    movie = sys.argv[9]
except IndexError:
    movie = "test_movie.txt"

currentFrame = 0
frame_deque = collections.deque(maxlen=30)
frame_list = []
frame_list_max = 2
frame_times = []
RTT = []
requests_sent = collections.deque()
last_frame_num = -1

# initialize frame deque (buffer)
#while len(frame_deque) != frame_deque.maxlen:


"""message = ereate_request_array(currentFrame, movie)
sock.sendto(message, server)"""
last_frame = current_milli_time()
# pre buffer
def buffering():
    while len(frame_deque) != frame_deque.maxlen:
        read_sockets, write_sockets, error_sockets = select.select([x[1] for x in active_server_list], [], [], 0)
        for s in read_sockets:
            if s == sock1 or s == sock2 or s == sock3 or s == sock4:
                receive_data(frame_list, last_frame_num, s)
        fill_list(frame_deque, frame_list, last_frame_num, requests_sent)
        add_to_deque(frame_deque, frame_list, last_frame_num, requests_sent)


buffering()
last_frame = current_milli_time()
# main loop
while currentFrame <= 30000:

    diff = current_milli_time() - last_frame
    if diff >= 10:
        try:
            frame = frame_deque.pop()
            if len(frame_deque) == 0:
                last_frame_num = frame.frame_num
        except IndexError:
            print("\n\n\!!!!!\tTrying to print frame, but no frame to print\t!!!!!!\n\n")
            frame = None
        if frame:
            frame_times.append(diff)
            last_frame = current_milli_time()
            currentFrame = frame.frame_num + 1
            print("\n\t\tDisplaying Frame {} Time: {}".format(frame.frame_num, diff))

    temp = current_milli_time()
    # read data if its available
    read_sockets, write_sockets, error_sockets = select.select([x[1] for x in active_server_list], [], [], 0)
    for s in read_sockets:
        if s == sock1 or s == sock2 or s == sock3 or s == sock4:
            receive_data(frame_list, last_frame_num, s)
    temp = temp - current_milli_time()
    #print("Read sockets time: {}".format(temp))

    temp = current_milli_time()
    # request more than one frame in a row
    fill_list(frame_deque, frame_list, last_frame_num, requests_sent)
    temp = temp - current_milli_time()
    #print("Fill list time: {}".format(temp))

    # check if deque needs to be filled
    temp = current_milli_time()
    if len(frame_deque) != frame_deque.maxlen:
        add_to_deque(frame_deque, frame_list, last_frame_num, requests_sent)
    temp = temp - current_milli_time()
    #print("Add to deque time: {}".format(temp))

    process_commands(commands)

    print(active_server_list)
    print(global_server_list)


frame_times.sort(reverse=True)
# print(frame_times)

# for x in range(1, len(frame_times)):
#	print("{},{}".format(x+2, sum(frame_times[:x])/float(10*len(frame_times[:x]))))


RTT.sort(reverse=True)
print "RTT {}".format(RTT)
print "RTT AVG: {}".format(sum(RTT)/float(len(RTT)))
print "in order: {}".format(inorder)
print "out of order: {}".format(ooorder)
print ("S30000 : {}".format(sum(frame_times)/ float(len(frame_times))))
print ("S2 : {}".format(sum(frame_times[:2])/ float(2)))
print ("S10 : {}".format(sum(frame_times[:10])/ float(10)))
print ("S20 : {} len(FT):  {}".format(sum(frame_times[:20])/ float(20), len(frame_times[:20])))
print ("S100 : {} len(FT):  {}".format(sum(frame_times[:100])/ float(100), len(frame_times[:100])))
control_stop.set()

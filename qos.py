import time
import socket
import sys


class QoS:
    def __init__(self, lock, global_server_list, active_server_list):
        self.lock = lock
        self.global_server_list = global_server_list
        self.active_server_list = active_server_list
        self.SOCKET_TIMEOUT = 0.01
        self.REPEAT_TIMEOUT = 0.1
        self.data = ''
        self.start()

    def start(self):
        while True:
            for i in self.global_server_list:
                # start = time.clock()
                i[1].sendto(self.create_request_array(9999, "test_movie.txt"), i[0])
                i[1].settimeout(self.SOCKET_TIMEOUT)
                try:
                    self.receive_data(i[1])
                except socket.timeout:
                    if i in self.active_server_list:
                        print("Server removed from active list: " + str(i[0]))
                        self.active_server_list.remove(i)
                    continue
                if i not in self.active_server_list:
                    print("Server added to active list: " + str(i[0]))
                    self.active_server_list.append(i)
                time.sleep(self.REPEAT_TIMEOUT)

    @staticmethod
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

    def receive_data(self, socket):
        #global data
        bytes_received = len(self.data)
        self.data += socket.recvfrom(1029-bytes_received)[0]
        frame_number = 0000
        if len(self.data) >= 1029:
            frame_number = int(self.data[:5].split(b'\0', 1)[0])
            # frame_data = data[6:1029].split(b'\0', 1)[0]
            if len(self.data) > 1029:
                self.data = self.data[1030:]
            else:
                self.data = ""
        if frame_number == "9999":
            return True
        return False

if __name__ == "__main__":
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
    global_server_list = [(server1, sock1), (server2, sock2), (server3, sock3), (server4, sock4)]
    active_server_list = [(server1, sock1), (server2, sock2), (server3, sock3), (server4, sock4)]
    qos = QoS("lock", global_server_list, active_server_list)
    qos.start()

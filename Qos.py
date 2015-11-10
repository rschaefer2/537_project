import time

class Gos:
    def __init__(self, lock, main_list, active_list):
        self.lock = lock
        self.main_list = main_list
        self.active_list = active_list
        self.THRESHOLD = 10

    def start(self):
        while True:
            for i in self.main_list:
                start = time.clock()
                # Send QoS message
                i[1].sendto(self.create_request_array(9999, "QoS_test"), i[0])
                # Receive QoS message
                self.receive_data(i[0])
                delay = time.clock() - start
                if delay > self.THRESHOLD:
                    self.active_list.remove(i)
                else:
                    if i not in self.active_list:
                        self.active_list.append(i)

    def create_request_array(self, frame_number, movie_title):
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
        global data
        bytes_received = len(data)
        data += socket.recvfrom(1029-bytes_received)[0]
        if len(data) >= 1029:
            frame_number = int(data[:5].split(b'\0', 1)[0])
            # frame_data = data[6:1029].split(b'\0', 1)[0]
            if len(data) > 1029:
                data = data[1030:]
            else:
                data = ""
        if frame_number == "9999":
            return True
        return False

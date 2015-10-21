class Frame:
    frame_num = 0
    data = b'\x00' * 1024

    def __init__(self, frame_num, data):
        self.frame_num = frame_num
        self.data = data


class FrameBuffer:
    BUFFER_SIZE = 31
    currentIndex = -1
    firstFrameIndex = -1
    lastFrameIndex = -1
    framebuf = []

    # switch direction of buffer. forward is decreasing vs increasing
    # def switch_dir():
    def __init__(self, size=31):
        self.BUFFER_SIZE = size
        self.framebuf = [Frame(-1, b'\x00') for _ in range(self.BUFFER_SIZE)]
        return

    # adds frame to the front of the buffer and alters indexes to match
    def addFrame(self, newFrame):
        if (self.firstFrameIndex >= 0):
            front = self.framebuf[self.firstFrameIndex % 31]
        else:
            front = self.framebuf[0]
        # only add frame, if it is within 4 of the front frame. Don't want to add too far past the front.
        if (newFrame.frame_num > front.frame_num and newFrame.frame_num <= front.frame_num + 5):
            newIndex = (newFrame.frame_num - front.frame_num + self.firstFrameIndex) % self.BUFFER_SIZE
            self.framebuf[newIndex] = newFrame
        else:
            print("Not Added {}\n".format(newFrame.frame_num))  # debug statement
            return False

        # if newframe is in front of the rear index, increment rear index to one past this frame.
        # won't work adding out of order packets around end of frame buffer
        if (newIndex >= self.lastFrameIndex):
            # increment until we find a valid frame
            tempIndex = newIndex + 1
            while (1):
                if (self.framebuf[(tempIndex) % self.BUFFER_SIZE].frame_num >= 0):
                    self.lastFrameIndex = (tempIndex) % self.BUFFER_SIZE
                    break
                else:
                    tempIndex += 1

        # increment front index while frame numbers increment by one
        # can't blindly increment on adding packet, since allow out of order adding
        while (1):
            next = (self.firstFrameIndex + 1) % self.BUFFER_SIZE
            if (self.framebuf[next].frame_num == self.framebuf[self.firstFrameIndex].frame_num + 1):
                self.firstFrameIndex = next
            else:
                break

        # debug statements
        print("Front:\t{}\tFrame {}".format(self.firstFrameIndex, self.framebuf[self.firstFrameIndex].frame_num))
        print("Back:\t{}\tFrame {}\n".format(self.lastFrameIndex, self.framebuf[self.lastFrameIndex].frame_num))
        print("Current:\t{}\tFrame {}\n".format(self.currentIndex, self.framebuf[self.currentIndex].frame_num))
        self.print_buf()
        return True


    def next_frame(self):
        """returns the next frame if valid and advances current index
        otherwise return None
        """
        nextIndex = (self.currentIndex + 1) % self.BUFFER_SIZE
        if nextIndex <= self.firstFrameIndex:
            self.currentIndex = (self.currentIndex + 1) % self.BUFFER_SIZE
            return self.framebuf[nextIndex]
        else:
            return None


    # for debugging
    def print_buf(self):
        for i in range(self.BUFFER_SIZE):
            print("{} |".format(self.framebuf[i].frame_num)),
        print("")

"""
# Test Code for proving functionality
circ_buffer = FrameBuffer()
# in order insertion
for i in range(35):
    f = Frame(i, b'\x00')
    circ_buffer.addFrame(f)

# out of order
list = [35, 37, 38, 39, 40, 36]
for i in list:
    f = Frame(i, b'\x00')
    circ_buffer.addFrame(f)
"""

import threading, collections

def command_control(commands):
    while 1:
        command = raw_input("Please enter a command: ")
        commands.append(command)

        if command.startswith("q"):
            break

def pause(commands):
    while 1:
        try:
            command = commands.pop()
        except IndexError:
            command = None
        if command and command.startswith("p"):
            break

def process_commands(commands):
    try:
        command = commands.pop() # don't block
    except IndexError:
        command = None

    if command:
        if command.startswith("p"):
            pause(commands)
        else:
            command = command.split(" ")
            if command[0].startswith("f"):
                print command[1]
                print type(command[1])
                print int(command[1])
                print type(int(command[1]))

commands = collections.deque()

control = threading.Thread(None, command_control, None, (commands, ), {})
control.start()
while 1:
    process_commands(commands)
    print "lllloooooooppp"

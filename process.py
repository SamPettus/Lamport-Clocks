import socket
import sys
import threading
from queue import Queue
HEADERSIZE = 10
def initializeSocket(portNum):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP socket
    s.connect((socket.gethostname(), portNum))
    return s

def recieve(s, q):
    while True:
        full_msg = ''
        new_msg = True
        while True: #Buffers data
            msg = s.recv(16) #Determines chunk size
            if new_msg:
                print(f"new message length: {msg[:HEADERSIZE]}")
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            full_msg += msg.decode("utf-8")

            if len(full_msg) - HEADERSIZE == msglen:
                print("full msg recieved!")
                print(full_msg[HEADERSIZE:])
                full_msg = "recieve," + full_msg[HEADERSIZE:]
                q.put(full_msg)
                new_msg = True
                full_msg = ''


        print(full_msg)#Byte SOCK_STREAM

def processingThread(q, lamportClock, s, processID):
    counter = 0
    while True:
        if not q.empty():
            msg = q.get()
            events = msg.split(",")
            if events[0] == "send":
                counter += 1
                lamportClock.append(counter)
                sendMsg = events[1] + "," + str(counter) +"," + events[2]
                sendMsg = f'{len(sendMsg):<{HEADERSIZE}}' + sendMsg
                s.send(bytes(sendMsg, "utf-8"))
            elif events[0] == "local":
                counter += 1
                lamportClock.append(counter)
            elif events[0] == "recieve":
                counter = max(int(events[1]), counter) + 1
                lamportClock.append(counter)
                print("{0} recieve event: recieve message(\"{1}\") from {2}".format(processID, events[3], events[2]))

def main():
    #Initial LamportClock State
    lamportClock = []
    q = Queue()
    #Gets port number from command line
    portNum = int(sys.argv[1])
    s = initializeSocket(portNum)
    #Creates communication thread
    communication = threading.Thread(target=recieve, args=(s,q ))
    communication.start()
    #Connection Message
    processing = threading.Thread(target=processingThread, args=(q, lamportClock, s, portNum))
    processing.start()

    while True:
        x = int(input('1 for Local Event, 2 for Communication event, and 3 for Print Clock: '))
        if x == 1:
            input('Process: ' + str(portNum) + ' Local Event: ')
            msg = "local"
            q.put(msg)
        if x == 2:
            destination, value = input('Process: ' + str(portNum) + ' Send Event: ').split()
            msg = "send," + destination + "," + value
            q.put(msg)
        if x == 3:
            print(lamportClock)



main()

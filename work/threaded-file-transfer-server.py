#! /usr/bin/env python3

import socket, sys, re, os
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "threadedserver"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

pidAddr = {}                    # for active connections: maps pid->client addr 

if paramMap['usage']:
    params.usage()

def readFraming(connected):
    data = connected.recv(4)
    if len(data) == 0: return # done if nothing read
    name_size = int(data.decode())
    data = connected.recv(name_size)
    fdOut = os.open(data.decode(), os.O_CREAT | os.O_WRONLY) # NEW FILE
    data = connected.recv(4)
    file_size = int(data.decode())
    while 1:
        data = connected.recv(file_size)
        os.write(fdOut, data)
        if(len(data) == file_size):
            print("good length; breaking")
            sendMsg = "successfully received file".encode()
            while len(sendMsg):
                bytesSent = connected.send(sendMsg)
                sendMsg = sendMsg[bytesSent:0]
            break
        file_size -= len(data)
    
    os.close(fdOut)
    connected.shutdown(socket.SHUT_WR)
    sys.exit(0)

from threading import Thread

class Server(Thread):
    def __init__(self, sockName):
        Thread.__init__(self)
        self.sock, self.addr = sockName
    def run(self):
        print("new thread handling connection from ", self.addr)
        while True:
            payload = readFraming(self.sock)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
print(f"server listening at ip address {listenAddr} and port {listenPort}")
#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#s.settimeout(5) # block for no more than 5 secs
s.bind((listenAddr, listenPort))
s.listen(5)

while True:
    sockAddr = s.accept()
    server = Server(sockAddr)
    server.start()
#! /usr/bin/env python3

import socket, sys, re, os
sys.path.append("./lib")       # for params
import params

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50000"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    (('-f', '--file'), 'file', "README.md") # filename
    )

progname = "threadedclient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, file = paramMap["server"], paramMap["usage"], paramMap["file"]

if usage:
    params.usage()

# get the socket's params
try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)
addrFamily = socket.AF_INET
socktype = socket.SOCK_STREAM
addrPort = (serverHost, serverPort)

def frameFile(file):
    retval = ""
    try: 
        file_size = os.path.getsize(file)
    except OSError:
        os.write(2, ("Error, unable to get file %s\n" %file).encode())
        return retval
    name_size = len(file)
    fdIn = os.open(file, os.O_RDONLY)
    input = os.read(fdIn, 9999)
    retval = "{:04d}{}{:04d}{}".format(name_size, file, file_size, input.decode())
    os.close(fdIn)
    return retval

def send(s, archive):
    while len(archive):
        print("sending file archive")
        bytesSent = os.write(s.fileno(), archive) # we send it to the FD of the socket
        archive = archive[bytesSent:] # we can swap o.write for [socket].send if desired

def createSocket(af, st, ap):
    sock = socket.socket(af, st)
    if sock is None:
        print('couldn not open socket!')
        sys.exit(1)
    sock.connect(ap)
    return sock

from threading import Thread;
class Client(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        print("Client started running")
        sock = createSocket(addrFamily, socktype, addrPort)
        name = sock.getsockname()
        if file:
            archive = frameFile(file)
            archive = archive.encode()
        sock.shutdown(socket.SHUT_WR)
        sock.close()
        print(f"Client {name} finished")

clients = [Client() for _ in range(10)]
for c in clients: 
    c.start()
for c in clients:
    c.join()
#! /usr/bin/env python3

import socket, sys, re, time, os
sys.path.append("./lib")       # for params
import params

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50000"),
    (('-d', '--delay'), 'delay', "0"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    (('-f', '--file'), 'file', "README.md") # filename
    )

progname = "frameClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, file = paramMap["server"], paramMap["usage"], paramMap["file"]

if usage:
    params.usage()

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

def createSocket(server):
    try:
        serverHost, serverPort = re.split(":", server)
        serverPort = int(serverPort)
    except:
        print("Can't parse server:port from '%s'" % server)
        sys.exit(1)
    
    s = None
    for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res # the five-tuple
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error as msg:
            print("    error: %s" % msg)
            s = None
            continue
        try:
            print("    attempting to connect to %s ..." % repr(sa))
            s.connect(sa)
        except socket.error as msg:
            print("    error: %s" % msg)
            s.close()
            s = None
            continue
        break
    
    if s is None: 
        print('could not open socket!!')
        sys.exit(1)
    return s

if file:
    archive = frameFile(file)
    print(archive)
    archive = archive.encode()

s = createSocket(server)

while len(archive):
    print("sending file archive")
    bytesSent = os.write(s.fileno(), archive) # we send it to the FD of the socket
    archive = archive[bytesSent:] # we can swap o.write for [socket].send if desired

s.shutdown(socket.SHUT_WR)

# delay before reading (default = 0s)
delay = float(paramMap['delay'])
if delay != 0:
    time.sleep(int(delay))

while 1:
    data = os.read(s.fileno(), 9999).decode()
    print("Received '%s'" % data)
    if len(data) == 0:
        break
print("zero length read. closing!")

s.close()
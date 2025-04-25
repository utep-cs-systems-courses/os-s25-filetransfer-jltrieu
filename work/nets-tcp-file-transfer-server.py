#! /usr/bin/env python3

import socket, sys, re, os, time
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


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
            break
        file_size -= len(data)
    
    os.close(fdOut)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"server listening at ip address {listenAddr} and port {listenPort}")
s.bind((listenAddr, listenPort))
s.listen(1) # only one request

conn, addr = s.accept()
print('Connected by ', addr)

readFraming(conn)

conn.shutdown(socket.SHUT_WR)
conn.close()
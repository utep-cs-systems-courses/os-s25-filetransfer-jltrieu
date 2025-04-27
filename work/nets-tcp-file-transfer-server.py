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
    connected.shutdown(socket.SHUT_WR)
    sys.exit(0)
    

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"server listening at ip address {listenAddr} and port {listenPort}")
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.settimeout(5) # block for no more than 5 secs
s.bind((listenAddr, listenPort))
s.listen(1) # only one request

while True:
    while pidAddr.keys():
        if(waitResult := os.waitid(os.P_ALL, 0, os.WNOHANG | os.WEXITED)):
            zPid, zStatus = waitResult.si_pid, waitResult.si_status
            del pidAddr[zPid]
        else:
            break
    
    try:
        connSockAddr = s.accept()
        print('Connected by ', connSockAddr)
    except TimeoutError:
        connSockAddr = None
    
    if connSockAddr is None:
        continue
    
    conn, addr = connSockAddr
    forkResult = os.fork()
    if (forkResult == 0):
        s.close() # child doesnt need this.
        readFraming(conn)
    
    conn.close()
    pidAddr[forkResult] = addr
    print(f"spawned off child with pid = {forkResult} at addr {addr}")
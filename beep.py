import sys

import ctypes
dll = ctypes.windll.user32


import socket
import sys
from thread import *

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port

def clientthread(conn):
    data = conn.recv(1024).rstrip()
    conn.close()

    if not data:
        dll.MessageBeep()
    else:
        try:
            title, message = data.split(':', 1)
        except:
            message = data
            title = 'remote'

        MB_ICONERROR   = 0x00000010
        MB_SYSTEMMODAL = 0x00001000
        dll.MessageBoxA(None, message, title, MB_ICONERROR | MB_SYSTEMMODAL)



def server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'Socket created'

    try:
        s.bind((HOST, PORT))
        print 'Socket bind complete'
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()


    s.listen(10)
    print 'Socket now listening'

    #now keep talking with the client
    while 1:
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])

        start_new_thread(clientthread ,(conn,))

    s.close()


if __name__ == '__main__':
    server()

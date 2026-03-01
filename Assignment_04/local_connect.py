import socket
import multiprocessing
import os

def local_server(address, port: int, sock_s: socket.socket, sock_c:socket.socket):
    is_executing = True
    sock_s.bind((address, port)) #port should match pynq client
    sock_s.listen()
    print('Waiting to connect to pynq client.')
    conn, addr = sock_s.accept()
    print('Connected local server to pynq client')
    while is_executing:
        data = conn.recv(1) # we only care about receiving 1 bytes
        print(f"Local server received data from pynq client: {data}")
        #send data to handler
        is_executing= client_handler(sock_c, data)

# funciton is responsible for sending message to connected client 
def client_handler(sock_c: socket.socket, data):
    #send data to server connectiion on pynq
    try:
        sock_c.sendall(data)
        if data == b'0':
            # close client disconnected
            print(f"Closing local server connection to pynq client.")
            sock_c.close()
            return False
        else:
            print(f"Local client handler sending data: {data}")
            return True
    except:
        sock_c.close()

def local_client(server_ip: str, port: int, sock_c: socket.socket):
    is_executing = True
    print(f"Connecting to pynq server: {server_ip}")
    sock_c.connect((server_ip, port)) # port should match pynq server
    print(f"Connected local client to pynq server!")
    while is_executing:
        #do nothing but stay connected 
        data = sock_c.recv(1)
        print(f"Data received by local client: {data}")
        if data == b'':
            is_executing = False
            print(f"Closing local client connection to pynq server.")
            sock_c.close()  
    sock_c.close()




if __name__ == '__main__':
    #set up sockets for local client and server

    procs = [] # a future list of all our processes
    PYNQ_CLIENT_PORT = 54321
    PYNQ_IP_ADDRESS = '192.168.2.99'
    PYNQ_SERVER_PORT = 12345
    # Launch local server process on CPU0
    sock_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p1 = multiprocessing.Process(target=local_server, args=('', PYNQ_CLIENT_PORT, sock_s, sock_c)) # the first arg defines which CPU to run the 'target' on
    p1.start() # start the process
    procs.append(p1)

    # Launch local client process on CPU1
    p2 = multiprocessing.Process(target=local_client, args=(PYNQ_IP_ADDRESS, PYNQ_SERVER_PORT, sock_c))
    p2.start() # start the process
    procs.append(p2)

    p1Name = p1.name # get process1 name
    p2Name = p2.name # get process2 name

    # Here we wait for process1 to finish then wait for process2 to finish
    p1.join() # wait for process1 to finish
    print('Process 1 with name, {}, is finished'.format(p1Name))

    p2.join() # wait for process2 to finish
    print('Process 2 with name, {}, is finished'.format(p2Name))

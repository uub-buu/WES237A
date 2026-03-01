#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pynq.overlays.base import BaseOverlay
import time, os, multiprocessing, socket, struct
from datetime import datetime
base = BaseOverlay("base.bit")
btns = base.btns_gpio


# In[2]:


get_ipython().run_cell_magic('microblaze', 'base.PMODB', '#include "gpio.h"\n#include "pyprintf.h"\n\n//Function to turn on/off a selected pin of PMODB\nvoid write_gpio(unsigned int pin, unsigned int val){\n    if (val > 1){\n        pyprintf("pin value must be 0 or 1\\n");\n    }\n    gpio pin_out = gpio_open(pin);\n    gpio_set_direction(pin_out, GPIO_OUT);\n    gpio_write(pin_out, val);\n}\n\n//Function to read the value of a selected pin of PMODB\nunsigned int read_gpio(unsigned int pin){\n    gpio pin_in = gpio_open(pin);\n    gpio_set_direction(pin_in, GPIO_IN);\n    return gpio_read(pin_in);\n}\n')


# In[3]:


def trigger_tone(data_pin: int, freq:float):
    ON = 1 
    OFF = 0
    
    if(freq <= 0.0):
        print("Error: Frequency must be greater than zero.")

    write_gpio(data_pin,ON)
    time.sleep(1.0 / (2.0 * freq))
    write_gpio(data_pin,OFF)
    time.sleep(1.0 / (2.0 * freq))


# In[4]:


def client_connect(ip: str, port: int, sock: socket.socket):
    tone_data = b'3' # we will be sending the integer representation of the pmod data data pin
    stop_data = b'0'
    connected = False
    button_pressed = False
    while True:
        #only process buttons when a new button is pressed
        #should handle debouncing
        value = btns.read()
        if value != 0 and button_pressed == False:
            button_pressed = True
            if value == 1: #0001
                # connect to server
                if not connected:
                    try:
                        sock.connect((ip, port))
                        connected = True
                        print(f"pynq client connected to local host server: {ip}")
                    except:
                        sock.close()
            if value == 2: #0010
                # send tone
                sock.sendall(tone_data)
            if value == 4: #0100
                # disconnect from server
                print(f"Closing connection to local client: {ip}")
                sock.sendall(stop_data)
                sock.close()
                break
        elif value == 0:
            button_pressed = False


# In[5]:


#server code
def server_connect(address, port: int, sock: socket.socket):
    # 1: Bind the socket to the pynq board <CLIENT-IP> at port <LISTENING-PORT>
    sock.bind((address, port))
    sock.listen(1)
    # 2: Accept connections
    conn, addr = sock.accept()
    print(f"Connected pynq server to local host client: 192.168.2.1")
    # 3: Receive bytes from the connection
    while True:
        data = conn.recv(1) # we only care about receiving 4 bytes
        # 4: Print the received message
        print(f"pynq server receiving data: {data}")
        if data == b'0':
            # client disconnected
            sock.close()
            print(f"Closing pynq server connection to local host client: 192.168.2.1")
            break
        if data == b'3':
            #extract data bit as integer value
            value = int(data.decode("ascii"))
            trigger_tone(value,0.5)
        
    sock.close()


# In[6]:


# multiproces code example
def main():
    procs = [] # a future list of all our processes

    # Launch process1 on CPU0
    sever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p1 = multiprocessing.Process(target=server_connect, args=('', 12345, sever_socket)) # the first arg defines which CPU to run the 'target' on
    os.system("taskset -p -c {} {}".format(0, p1.pid)) # taskset is an os command to pin the process to a specific CPU
    p1.start() # start the process
    procs.append(p1)

    # Launch process2 on CPU1
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p2 = multiprocessing.Process(target=client_connect, args=('192.168.2.1', 54321, client_socket)) # the first arg defines which CPU to run the 'target' on
    os.system("taskset -p -c {} {}".format(1, p2.pid)) # taskset is an os command to pin the process to a specific CPU
    p2.start() # start the process
    procs.append(p2)

    p1Name = p1.name # get process1 name
    p2Name = p2.name # get process2 name

    # Here we wait for process1 to finish then wait for process2 to finish
    p1.join() # wait for process1 to finish
    print('Process 1 with name, {}, is finished'.format(p1Name))

    p2.join() # wait for process2 to finish
    print('Process 2 with name, {}, is finished'.format(p2Name))


# In[7]:


main()


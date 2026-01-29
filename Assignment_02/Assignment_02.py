#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pynq.overlays.base import BaseOverlay
import threading
import time
from queue import PriorityQueue
from itertools import count
import pynq.lib.rgbled as rgbled

base = BaseOverlay("base.bit")
btn_0 = base.btns_gpio[0]

MAX_FORKS = 5
MAX_LEDS = 5
MAX_PHILOS = 5

#class handling philospher creation and states
class philosopher(object):
     
    def __init__(self, led_i):
        if (led_i not in range(0,MAX_LEDS)):
            raise ValueError("LED selected is out of range")
        if(led_i == 4):
            self.led = rgbled.RGBLED(led_i)
            #self.led = led(led_i)
        else:
            #self.led = led(led_i)
            self.led = base.leds[led_i]

        self._index = led_i
        print(f"Philosopher {led_i} is at the table")

    def run(self, left_fork:threading.Lock, right_fork:threading.Lock, allowed: bool):
        if allowed:
            left_fork.acquire()
            right_fork.acquire()
            # begin eating for a 5 sec duration
            self.eating(3)
            # once duraiton is finished,release fork resources
            left_fork.release()
            right_fork.release()
            # take a nap
            self.napping(1)
            time.sleep(0) #yield
        else:
            # otherwise we are starving.
            self.starving()



    #function to simulate eating
    def eating(self, duration):
        cycle_duration = 0.5
        #print(f"led{self._index} is eating\n")
        while(duration != 0):

            self._toggle(cycle_duration)
            duration -= cycle_duration
           
    #fucntion to simulate napping
    def napping(self, duration):
        cycle_duration = 1
        #print(f"led{self._index} is napping\n")
        while(duration != 0):
            self._toggle(cycle_duration)
            duration -= cycle_duration
   
    #function to simulate starving
    def starving(self):            
        #print(f"led{self._index} is starving\n")
        self.led.off()
   
    # toggle the led for a cycle of the specified duration            
    def _toggle(self, duration):
        if self._index == 4:
            self.led.on(0x02) # uncomment when working on pynq
            #self.led.on()
        else:
            self.led.on()
        time.sleep(duration/2)
        self.led.off()
        time.sleep(duration/2)


# In[3]:


# initialize the fork resources in question
forks = []
for fork in range(MAX_FORKS):
    fork = threading.Lock()
    forks.append(fork)

#initialize philosopher objects
philos = []
for p_index in range(MAX_PHILOS):
    p = philosopher(p_index)
    philos.append(p)

def monitor(philos: philosopher, left_fork:threading.Lock, right_fork:threading.Lock, button_event: threading.Event): #add threading.Event
    while not button_event.is_set(): # replace with threading.Event     
        # left and right are needed to eat
        if(not left_fork.locked() and not right_fork.locked()):
            allowed=True
        else:
            allowed =False

        philos.run(left_fork, right_fork, allowed)

def stop_button(button_event: threading.Event):
    #replace this logic with button stuff
    print("Use BTN0 to exit the program")
    while not button_event.is_set():
        if btn_0.read() != 0:
            print("Button 0 was pressed")
            button_event.set()


# In[4]:


threads = []
stop_button_event = threading.Event()
for i in range(len(philos)):
    if(i == 0):
        resources = (philos[i], forks[i], forks[len(philos)-1], stop_button_event)
    else:
        resources = (philos[i], forks[i], forks[i-1], stop_button_event)
    t = threading.Thread(target=monitor, args=resources)
    threads.append(t)

#rename to button task or button_job
button_thread = threading.Thread(target=stop_button, args=(stop_button_event,)) 
threads.append(button_thread)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()


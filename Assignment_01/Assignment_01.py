#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from pynq.overlays.base import BaseOverlay
import time
from datetime import datetime
base = BaseOverlay("base.bit")


# In[ ]:


get_ipython().run_cell_magic('microblaze', 'base.PMODB', '\n#include "gpio.h"\n#include "pyprintf.h"\n\n//Function to turn on/off a selected pin of PMODB\nvoid write_gpio(unsigned int pin, unsigned int val){\n    if (val > 1){\n        pyprintf("pin value must be 0 or 1\\n");\n    }\n    gpio pin_out = gpio_open(pin);\n    gpio_set_direction(pin_out, GPIO_OUT);\n    gpio_write(pin_out, val);\n}\n\n//Function to read the value of a selected pin of PMODB\nunsigned int read_gpio(unsigned int pin){\n    gpio pin_in = gpio_open(pin);\n    gpio_set_direction(pin_in, GPIO_IN);\n    return gpio_read(pin_in);\n}\n')


# In[ ]:


import asyncio
cond = True

RED_BTN = 0
GREEN_BTN = 1
BLUE_BTN = 2
STOP_BTN = 3

BLUE_LED = 1
GREEN_LED = 2
RED_LED = 3
btns = base.btns_gpio
current_led = None

def reset_gpio():
    global current_led
    print("Resetting GPIOs\n")
    for pin in range(8):        
        write_gpio(pin,0)    
    current_led = None

async def pwm(pin, freq, duty_cycle, stop: asyncio.Event):
    global current_led
    print("STARTING PWM")
    if(duty_cycle < 0 or duty_cycle > 100):
        print("Duty cycle is invalid.\n")
        return
    # Default case during bootup
    while not stop.is_set():
        if(current_led == None):
            on_period = 1 # 1 sec on
            off_period = 1 # 1 sec off
        else:
            pin = current_led
            period = 1/freq
            on_period = period*(duty_cycle/100)
            off_period = period - on_period
            #edge case that duty cycle is 0% then led will not be on T_off = T_period
        if(duty_cycle != 0):    
            write_gpio(pin, 1) # turn pin on for certain duration
        await asyncio.sleep(on_period)
        #edge case that duty cycle is 100% then led will be on T_on = T_period
        if(duty_cycle != 100):
            write_gpio(pin, 0) # turn pin off for certain duration
        await asyncio.sleep(off_period)
    
async def btns_status(_loop, stop: asyncio.Event):
    global current_led
    while not stop.is_set():
        await asyncio.sleep(0.1)
        if btns[RED_BTN].read() != 0:
            current_led = RED_LED
        if btns[GREEN_BTN].read() != 0:
            current_led = GREEN_LED
        if btns[BLUE_BTN].read() != 0:
            current_led = BLUE_LED
        if btns[STOP_BTN].read() != 0:
            stop.set()
            reset_gpio()
            _loop.stop()
            cond = False
            
#function to allow pwm to continue until stop event is detected. 
async def demo_pwm(led, freq, duty_cycle):
    global current_led
    
    current_led = led
    print(f"call from demo_pwm: {duty_cycle}%")
    stop = asyncio.Event()
    task = asyncio.create_task(pwm(current_led, freq, duty_cycle, stop))
    await asyncio.sleep(5)
    stop.set()
    await task 
    await asyncio.sleep(2)

        


# In[ ]:


# run this code to demonstrate varying duty cycle for 25% must reset kernel
reset_gpio()
duty_cycle_loop = asyncio.new_event_loop()
asyncio.set_event_loop(duty_cycle_loop)
duty_cycle_loop.run_until_complete(demo_pwm(RED_LED, 500, 25))
duty_cycle_loop.close()


# In[ ]:


# run this code to demonstrate varying duty cycle for 50% must reset kernel
reset_gpio()
duty_cycle_loop = asyncio.new_event_loop()
asyncio.set_event_loop(duty_cycle_loop)
duty_cycle_loop.run_until_complete(demo_pwm(RED_LED, 500, 50))
duty_cycle_loop.close()


# In[ ]:


# run this code to demonstrate varying duty cycle for 75% must reset kernel
reset_gpio()
duty_cycle_loop = asyncio.new_event_loop()
asyncio.set_event_loop(duty_cycle_loop)
duty_cycle_loop.run_until_complete(demo_pwm(RED_LED, 500, 75))
duty_cycle_loop.close()


# In[ ]:


# run this code to demonstrate varying duty cycle for 100% must reset kernel
reset_gpio()
duty_cycle_loop = asyncio.new_event_loop()
asyncio.set_event_loop(duty_cycle_loop)
duty_cycle_loop.run_until_complete(demo_pwm(RED_LED, 500, 100))
duty_cycle_loop.close()


# In[ ]:


#this portion of the code is to demonstrate button events to toggle the LED color
stop_event = asyncio.Event()
reset_gpio()
loop = asyncio.new_event_loop()
loop.create_task(pwm(RED_LED, 5, 25, stop_event))
loop.create_task(btns_status(loop, stop_event))
loop.run_forever()
loop.close()
print("DONE.")


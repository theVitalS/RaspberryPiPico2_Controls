from machine import Pin, PWM
import time
import random

# Define the GPIO pins for motor control
lf = Pin(13, Pin.OUT)
lb = Pin(12, Pin.OUT)
rf = Pin(11, Pin.OUT)
rb = Pin(10, Pin.OUT)

'''
ENA = PWM(Pin(17))
ENB = PWM(Pin(16))# PWM pin for speed control (ENA)

# Set PWM Frequency
ENA.freq(1000)          # Set frequency to 1kHz
ENB.freq(1000)  

#standard_speed = 50
speed = 20
ENA.duty_u16(int(speed * 65535 / 100))
ENB.duty_u16(int(speed * 65535 / 100))



def both_speed(sp=speed):
    ENA.duty_u16(int(sp * 65535 / 100))
    ENB.duty_u16(int(sp * 65535 / 100))
    
def left_speed(sp=speed):
    ENB.duty_u16(int(sp * 65535 / 100))

def both_speed(sp=speed):
    ENA.duty_u16(int(sp * 65535 / 100))
    

def slight_right(sp=speed, t=1):
    right_seed(0.7*sp)   
    time.sleep(t)
    right_seed(sp)
    
    
def slight_left(sp=speed, t=1):
    left_seed(0.7*sp)   
    time.sleep(t)
    left_seed(sp)  
'''




def left_forward():
    #print('left_forward')
    lb.low()
    lf.high()
    
    
def right_forward():
    #print('right_forward')
    rb.low()
    rf.high()
    
    
def left_backward():
    #print('left_backward')
    lf.low()
    lb.high()
    
    
def right_backward():
    #print('right_backward')
    rf.low()
    rb.high()
    


def move_forward():
    left_forward()
    right_forward()





def move_backward():
    left_backward()
    right_backward()


def turn_left(n=1.5):
    left_backward()
    right_forward()
    time.sleep(n)
    stop()
    
    
def turn_right(n=1.5):
    left_forward()
    right_backward()
    time.sleep(n)
    stop()

def stop():
    lf.low()
    lb.low()
    rf.low()
    rb.low()
    
    
def random_turn():
    rot = random.uniform(0.3, 2)
    dir = random.randint(1, 2)
    if dir == 1:
        turn_right(rot)
    else:
        turn_left(rot)

def test1():
    stop()
    time.sleep(0.5)
    move_forward()
    time.sleep(1)
    stop()
    time.sleep(1)
    move_backward()
    time.sleep(1)
    stop()
    turn_left()
    time.sleep(1)
    turn_right()
    time.sleep(1)
    move_forward()
    time.sleep(1)
    stop()
    time.sleep(1)
    move_backward()
    time.sleep(1)
    stop()
    
    
def test2():
    stop()
    time.sleep(0.5)
    move_forward()
    time.sleep(1)
    stop()
    time.sleep(1)
    move_backward()
    time.sleep(1)
    stop()
    turn_left()
    time.sleep(1)
    turn_right()
    stop()
    
    
   
def test3 (x):
    i = 0
    while i < x:

        move_forward()
        time.sleep(1)
        stop()
        time.sleep(2)
        
        # Example: Turn left for 1 second, then stop
        move_backward()
        time.sleep(1)
        stop()
        time.sleep(1)
        i += 1



from machine import Pin, PWM
import random
import time
from car import *
from HC_SR04_distance_sensor import *
    

ENA = PWM(Pin(17))
ENB = PWM(Pin(16))# PWM pin for speed control (ENA)

# Set PWM Frequency
ENA.freq(1000)          # Set frequency to 1kHz
ENB.freq(1000)  

#standard_speed = 50
speed = 70
ENA.duty_u16(int(speed * 65535 / 100))
ENB.duty_u16(int(speed * 65535 / 100)) 


stop()
time.sleep(2)
    

def main(n = 40, random_stops=False):
    reps = 0
    while reps < n:
        
        distance = get_distance()       
        if not distance:
            print("Distance measurement failed. Stopping robot.")
            stop()
            return
        print("Distance: {:.2f} cm".format(distance))
        
        start_time = time.time()
        
        while distance > 30:
            move_forward()
            time.sleep(0.01)
            
            distance = get_distance(500)
            print("Distance: {:.2f} cm".format(distance))

            
            if random_stops:
                current_time = time.time()
                t = current_time-start_time
                if t <= random.randint(3, 6):
                    print('Go random turn')
                    random_turn()
                    
            
            
            
        stop()
        time.sleep(1)
        
        move_backward()
        time.sleep(0.6)
        
        stop()
        time.sleep(1)
        
        random_turn()
                  
        reps += 1
        

def disco():
    freq = [2,3]
    while True:
        for f in freq:
            turn_right(f)
            stop()
            time.sleep(0.3)
            turn_left(f)
            stop()
            time.sleep(0.3)
    

main()
#hc_sr04_example_usage()   
    
    
    
    
    




#!/usr/bin/env python3
import pygame
import sys
import random
import math

pygame.init()
pygame.joystick.init()

from pygame import mixer

engine = pygame.mixer.Sound('sodastream.mp3')

# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

# Setting up color objects
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
font = pygame.font.Font(None, 32)
gameoverfont = pygame.font.Font(None, 100)

def relative_moon_gravity(height):
    moon_gravity = 1.625 #m/s**2
    moon_radius = 17380 #meters
    return (moon_gravity * (moon_radius /(moon_radius + height))**2)

height = 10000
ground = int(height/10) #10000 meters
wall_to_wall = 1200
tick_duration_seconds = 1

disp = pygame.display.set_mode((wall_to_wall,ground))
disp.fill(BLACK)
pygame.display.set_caption("Lunar lander")

moon = pygame.image.load("moon.jpeg")
disp.blit(moon, (0,ground-30))

joystick_count = pygame.joystick.get_count()
print("Number of joysticks : %d" %(joystick_count))
if (joystick_count>0):
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Joystick name : %s" % (joystick.get_name()))
    num_axes = joystick.get_numaxes()
    num_buttons = joystick.get_numbuttons()
else:
    print("ERROR, NO JOYSTICK CONNECTED")


class Lander(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.angle = 90
        self.h_speed = 400/3.6 #m/s, should be 6000/3.6
        self.v_speed = 0
        self.mass = 7327 #kg
        self.max_thrust = 45.04*1000 #N
        self.time = 0
        self.h_accel = 0
        self.v_accel = 0
        self.fuel = 2000
        self.thrust = 0
        self.thrust_active = 0
        self.h_speed_limit = 10
        self.v_speed_limit = 40
        self.angle_limit = 2
        self.relative_gravity = relative_moon_gravity(height)
        self.image = pygame.image.load("lunar_lander.png")
        self.surf = pygame.Surface((100,84))
        self.rect = self.surf.get_rect(center = (random.randint(int(200),int(wall_to_wall/2+100)),50))
        self.lander = pygame.transform.rotate(self.image, self.angle)
    
    def update_gravity(self):
        self.relative_gravity = relative_moon_gravity(height - self.rect.center[1]*10)
        #print("Center : %s , relative moon gravity : %f" %(str(self.rect.center), self.relative_gravity))
    
    def move(self):
        delta_vertical_dist = self.v_speed * tick_duration_seconds + 0.5 * (self.relative_gravity + self.v_accel) * (tick_duration_seconds**2)
        delta_horizontal_dist = self.h_speed * tick_duration_seconds + 0.5 * self.h_accel * (tick_duration_seconds**2)
        self.v_speed = delta_vertical_dist/tick_duration_seconds
        self.h_speed = delta_horizontal_dist/tick_duration_seconds
        #print("Vertical distance : %f (%f pixels)" %(delta_vertical_dist, delta_vertical_dist/10))
        #print("Horizontal distance : %f (%f pixels)" %(delta_horizontal_dist, delta_horizontal_dist/10))
        self.rect.move_ip(int(delta_horizontal_dist/10),int(delta_vertical_dist/10))
        if (self.rect.bottom > (ground-30)):
            print("ANGLE: %f, VERTICAL SPEED : %f, HORIZONTAL SPEED : %f" %(self.angle, self.v_speed, self.h_speed))
            if ((abs(self.angle) < self.angle_limit) and (self.v_speed < self.v_speed_limit) and (abs(self.h_speed) < self.h_speed_limit) and
                self.rect.centerx>530 and self.rect.centerx<600):
                print("THE EAGLE HAS LANDED")
                word = "THE EAGLE HAS LANDED"
                text = gameoverfont.render(word, True, WHITE, GREEN)
            else:
                print("FAILURE, YOU ARE DEAD")
                word = "MISSION FAILURE"
                text = gameoverfont.render(word, True, WHITE, RED)
            text_height = text.get_height()
            text_width = text.get_width()
            disp.blit(text, (int(wall_to_wall/2-text_width/2), (int(ground/2-text_height/2))))
            print("CENTER X : %d"%(self.rect.centerx))
            return False
        else:
            return True
    
    def draw(self, surface):
        surface.blit(self.lander, self.rect)
        
    def update_accel(self):
        self.h_accel = -(math.sin(self.angle * math.pi/180)*self.thrust*self.thrust_active)/self.mass
        self.v_accel = -(math.cos(self.angle * math.pi/180)*self.thrust*self.thrust_active)/self.mass
        #print("Update accel, thrust : %f, angle : %d, h_accel : %f, v_accel : %f" %(self.thrust, self.angle, self.h_accel, self.v_accel))
        
    def update_thrust(self, percent_thrust):
        if (percent_thrust >=0):
            self.thrust = percent_thrust*self.max_thrust
            engine.set_volume(percent_thrust/2)
        
    def update_thrust_active(self, active):
        if (self.fuel > 0):
            self.thrust_active = active
            if (active):
                engine.play()
            else:
                engine.stop()
        else:
            self.thrust_active = 0
            mixer.music.stop()
        
    def update_fuel(self):
        if (self.thrust_active):
            self.fuel = self.fuel - self.thrust/5000
        
    def update_angle(self, angle):
        if (abs(angle) < 0.1):
            angle = 0
        self.angle = self.angle - angle*2
        #print("New angle: %f, input angle : %f" %(self.angle, pos))
        self.lander = pygame.transform.rotate(self.image, self.angle)

    def draw_dashboard(self):
        word = "H SPEED : %04.2f" %(self.h_speed/10)
        if (abs(self.h_speed) > self.h_speed_limit):
            text = font.render(word, True, RED, WHITE)
        else:
            text = font.render(word, True, GREEN, WHITE)
        text_height = text.get_height()
        disp.blit(text, (0, 0))
        word = "V SPEED : %04.2f" %(self.v_speed/10)
        if (self.v_speed > self.v_speed_limit):
            text = font.render(word, True, RED, WHITE)
        else:
            text = font.render(word, True, GREEN, WHITE)
        disp.blit(text, (0, text_height))
        
        word = "ANGLE   : %04.2f" %(self.angle)
        if (abs(self.angle)>self.angle_limit):
            text = font.render(word, True, RED, WHITE)
        else:
            text = font.render(word, True, GREEN, WHITE)
        disp.blit(text, (0, text_height*2))
        word = "FUEL    : %04.2f" %(self.fuel)
        if (self.fuel < 0):
            text = font.render(word, True, RED, BLACK)
        else:
            text = font.render(word, True, BLUE, WHITE)
        disp.blit(text, (0, text_height*3))
        word = "THRUST    : %04.2f" %(self.thrust/1000)
        text = font.render(word, True, BLUE, WHITE)
        disp.blit(text, (0, text_height*4))
        if (self.thrust_active):
            word = "THRUSTER ACTIVE"
            text = font.render(word, True, WHITE, RED)
        else:
            word = "THRUSTER IDLE"
            text = font.render(word, True, GREEN, WHITE)
        disp.blit(text, (0, text_height*5))
        word = "HEIGHT    : %04d" %(height-self.rect.center[1]*10)
        text = font.render(word, True, BLUE, WHITE)
        disp.blit(text, (0, text_height*6))
        word = "GRAVITY    : %04.2f" %(self.relative_gravity)
        text = font.render(word, True, BLUE, WHITE)
        disp.blit(text, (0, text_height*7))
        

Eagle = Lander()
loop = True
while loop:
    for event in pygame.event.get(): # Get events
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
            pygame.quit()
            sys.exit()
        else:
            press = joystick.get_button(1) #Get exit button
            if(press == 1): 
                pygame.quit()
                sys.exit()               
            press = joystick.get_button(0) #Get thruster
            Eagle.update_thrust_active(press) #Send 
    
    disp.fill(BLACK) #Clear screen
    pos = joystick.get_axis(0) #Get joystick position
    Eagle.update_gravity() #Update gravity according to height
    Eagle.update_angle(pos) #Send the joystick position to the object
    Eagle.update_thrust(joystick.get_axis(2)) #Update active thrust setting
    Eagle.update_accel() #Use acceleration
    Eagle.update_fuel() #Update fuel used
    loop = Eagle.move() #Move the eagle according to gravity, thrust active and thrust setting
    Eagle.draw_dashboard() #Draw dashboard
    Eagle.draw(disp) #Draw the Eagle
    disp.blit(moon, (0,ground-30))
    pygame.display.update() #Update display
    clock.tick(20)
    
while True:
    pygame.event.get()
    press = joystick.get_button(1)
    if(press == 1): #Get exit
        pygame.quit()
        sys.exit()
    clock.tick(20)


from math import *
from utility import *
import pygame
class Car:
    def __init__(self,angle,pos,image) :
        self.angularspeed=3
        self.speed=0
        self.theta=angle
        self.accelaration=2
        self.position=pos
        self.image=pygame.transform.scale(pygame.image.load(image),(pygame.image.load(image).get_width()/2,pygame.image.load(image).get_height()/2))
        self.car_mask=pygame.mask.from_surface(self.image)  #as it is multiplayer game i thaught it would be better to send mask data instead to find mask in local sytsem every time
    def move_for_back(self,Forw=True):
        if Forw:
            self.speed=min(self.speed+self.accelaration,5)
        else:
            self.speed=max(self.speed-self.accelaration,-5)
      
        
    def rotate(self,left=False,right=False):
        if self.speed!=0:
            if left:
                self.theta+=self.angularspeed 
            if right:
                self.theta-=self.angularspeed
    def decelarate(self):
        if self.speed>0:
            self.speed-=1
        elif self.speed<0:
            self.speed+=1
    def display_name(self,name):
        display(name,self.image,self.position)

    def collision(self,track_mask):
        pos=track_mask.overlap(self.car_mask,(int(self.top_left[0]),int(self.top_left[1])))
        return pos
    def bounce(self):
        self.speed=-1.5*self.speed
        self.position[1]-=self.speed*cos(radians(self.theta))
        self.position[0]-=self.speed*sin(radians(self.theta))
        self.decelarate()

    def draw(self,win):
        self.decelarate()
        self.position[1]-=self.speed*cos(radians(self.theta))
        self.position[0]-=self.speed*sin(radians(self.theta))
        mask_and_rotatedimage_rectpos=blit_rotate_center(win,self.image,self.position,self.theta)
        self.car_mask=mask_and_rotatedimage_rectpos[0]
        self.top_left=mask_and_rotatedimage_rectpos[1]
    def control(self):
        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rotate(True)
        if keys[pygame.K_RIGHT]:
            self.rotate(right=True)
        if keys[pygame.K_UP]:
            self.move_for_back()
        if keys[pygame.K_DOWN]:
            self.move_for_back(False)
        
        
        
    
class player:
    def __init__(self,name):
        self.car_list=["red-car.png"]
        self.name=name
        self.car=None
        self.coins=500
    def choose_car(self,image):
        self.car=Car(0,[50,80],image)
    
    
    
    

        




    
import pygame
import sys
from cars import player
from buttton_for_game import Button
class game:
    def __init__(self) -> None:
        self.run=True
        self.win_width=700
        self.win_hight=700
        self.car_list=["red-car.png","green-car.png","grey-car.png","purple-car.png"]
        self.car_price=[0,100,200,300]
        self.track_list={}
        self.player=None
    def input_name(self,win):
        if self.run:
            name = ""
            font = pygame.font.Font(None, 32)
            input_active = True
    
            while input_active:
                win.fill((255, 255, 255))
                text_surface = font.render("Enter your name: " + name, True, (0, 0, 0))
            
                
                win.blit(text_surface, (200, 330))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            name = name[:-1]
                        else:
                            name += event.unicode
            self.player=player(name)
    
        self.run=False
    def create_lobby(self,win):
        car_index=0
        name_surface = pygame.font.Font(None,32).render(self.player.name,True, (0, 0, 0))
        
        
    # Initialize buttons
        BLACK=[0,0,0]
        GRAY=[100,100,0]
        WHITE=[250,250,250]
    
        play_offline = Button("play offline", BLACK, GRAY, 75, 100, (450,600))
        play_online = Button("play online", BLACK, GRAY, 75, 100, (575,600))
        left_arrow= Button("<", BLACK, GRAY, 100, 100, (50,250))
        right_arrow= Button(">", BLACK, GRAY, 100, 100, (550,250))
        choose=Button("choose", BLACK, GRAY,75 , 100, (200,425))
        buy=Button("buy", BLACK, GRAY,75 , 100, (400,425))

    # Main loop
        running = True
        while running:
            coin_surface = pygame.font.Font(None,32).render("coin :" +str( self.player.coins),True, (0, 0, 0))
            coin_of_car= pygame.font.Font(None,32).render("coin :" +str( self.car_price[car_index]),True, (0, 0, 0))
            car_image=pygame.transform.scale(pygame.image.load(self.car_list[car_index]),(125,200))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if buttons are clicked
                    mouse_pos = pygame.mouse.get_pos()
                    if play_offline.is_button_pressed(mouse_pos) and self.player.car:
                        self.play_offline(win)
                    elif play_online.is_button_pressed(mouse_pos):#play online
                        pass
                    elif right_arrow.is_button_pressed(mouse_pos) and car_index<len(self.car_list)-1:
                        car_index+=1
                    elif left_arrow.is_button_pressed(mouse_pos) and car_index>0 :
                        car_index-=1
                    elif choose.is_button_pressed(mouse_pos) and self.car_list[car_index] in self.player.car_list:
                        self.player.choose_car(self.car_list[car_index])
                    elif buy.is_button_pressed(mouse_pos) and self.car_list[car_index] not in self.player.car_list :
                        if self.player.coins>=self.car_price[car_index]:
                            self.player.car_list.append(self.car_list[car_index])
                            self.player.coins-=self.car_price[car_index]
        
                            
                    

        # Draw buttons
            win.fill(WHITE)
            pygame.draw.rect(win,[250,250,0],pygame.Rect(200,200,300,200))
            win.blit(name_surface,(10,10))
            win.blit(coin_surface,(600,10))
            win.blit(car_image,(200,200))
            if self.car_list[car_index] not in self.player.car_list:
                buy.create_button(win)
            else:
                buy.is_created=False
            choose.create_button(win)
            play_offline.create_button(win)
            play_online.create_button(win)
            right_arrow.create_button(win)
            left_arrow.create_button(win)
            pygame.display.flip()
    def play_offline(self,win):
        clock=pygame.time.Clock()
        track_mask=pygame.transform.scale(pygame.image.load("track-border.png"),(700,700))
        track_mask=pygame.mask.from_surface(track_mask)
        track=pygame.transform.scale(pygame.image.load("track.png"),(700,700))
        
        run=True

        while run:
    
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    run=False
                    sys.exit()
                if event.type==pygame.MOUSEBUTTONDOWN:
                    position=pygame.mouse.get_pos()
            
            self.player.car.control()
            win.fill([250,250,250])
            win.blit(track,[0,0])
            self.player.car.draw(win)
    
            if self.player.car.collision(track_mask):
                
                self.player.car.bounce()
        
        
            clock.tick(60)
    
            pygame.display.update()
    def play_online(self,win):
        clock=pygame.time.Clock()
        track_mask=pygame.transform.scale(pygame.image.load("track-border.png"),(700,700))
        track_mask=pygame.mask.from_surface(track_mask)
        track=pygame.transform.scale(pygame.image.load("track.png"),(700,700))
        
        run=True

        while run:
    
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    run=False
                    sys.exit()
                if event.type==pygame.MOUSEBUTTONDOWN:
                    position=pygame.mouse.get_pos()
            
            self.player.car.control()
            win.fill([250,250,250])
            win.blit(track,[0,0])
            self.player.car.draw(win)
    
            if self.player.car.collision(track_mask):
                
                self.player.car.bounce()
        
        
            clock.tick(60)
    
            pygame.display.update()
    


        


    


        

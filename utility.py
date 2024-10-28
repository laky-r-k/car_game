import pygame
def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)  
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)
    return (pygame.mask.from_surface(rotated_image),new_rect.topleft)
def display(text,win,pos):
    font_o=pygame.font.SysFont("BOLD",50)
    surface=pygame.font.Font.render(font_o,text,True,[0,0,0])
    win.blit(surface,pos)
    


    
        

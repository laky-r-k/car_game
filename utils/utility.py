import pygame

def blit_rotate_center(surface, image, position, angle):
    """
    Rotates an image around its center and blits it to the surface.
    Returns:
        - mask: pygame.Mask for collision detection
        - top_left: top-left position of the rotated image
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=position).center)
    surface.blit(rotated_image, new_rect.topleft)

    # Create a mask from the rotated image
    mask = pygame.mask.from_surface(rotated_image)

    return mask, new_rect.topleft

def display(text, surface, position, font_size=24, color=(0, 0, 0)):
    """
    Draws text on the surface at the given position.
    """
    font = pygame.font.Font(None, font_size)
    rendered_text = font.render(text, True, color)
    surface.blit(rendered_text, position)

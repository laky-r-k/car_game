import pygame
from utils.utility import blit_rotate_center

class CarRenderer:
    def __init__(self, image_path):
        """
        Handles rendering and collision mask generation for a car.
        """
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(
            self.original_image,
            (self.original_image.get_width() // 2, self.original_image.get_height() // 2)
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.top_left = (0, 0)  # updated on each draw

    def draw(self, surface, position, angle):
        """
        Draws the car on the given surface at position (x, y) and angle (in degrees).
        Also updates the mask and top-left corner for collision.
        """
        self.mask, self.top_left = blit_rotate_center(surface, self.image, position, angle)

    def get_mask_bits(self):
        """
        Returns a 2D list of 0s and 1s representing the car mask.
        Useful for sending to server.
        """
        width, height = self.mask.get_size()
        return [[self.mask.get_at((x, y)) for x in range(width)] for y in range(height)]

    def export_mask_compressed(self):
        """
        Returns a compressed (zlib) version of the mask bit array.
        """
        import zlib, pickle
        return zlib.compress(pickle.dumps(self.get_mask_bits()))

    def update_image(self, new_image_path):
        """
        Change the car image dynamically (e.g. for skin switching).
        """
        self.original_image = pygame.image.load(new_image_path).convert_alpha()
        self.image = pygame.transform.scale(
            self.original_image,
            (self.original_image.get_width() // 2, self.original_image.get_height() // 2)
        )
        self.mask = pygame.mask.from_surface(self.image)

from cars.car import Car
from math import atan2, degrees, radians, sin, cos
import numpy as np
import math


class AICar(Car):
    def __init__(self, angle, pos, waypoints):
        super().__init__(angle, pos)
        self.path = waypoints
        self.current_point = 0
        self.max_speed=2

    
    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.position[0]
        y_diff = target_y - self.position[1]

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.position[1]:
            desired_radian_angle += math.pi

        difference_in_angle = self.theta - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.theta -= min(self.angular_speed, abs(difference_in_angle))
        else:
            self.theta += min(self.angular_speed, abs(difference_in_angle))
    def get_current_point(self):
        return self.path[self.current_point]
    def update_path_point(self,):
        self.current_point += 1

    def aimove(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.move_forward()
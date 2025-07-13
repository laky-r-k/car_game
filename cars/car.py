from math import sin, cos, radians

class Car:
    def __init__(self, angle, pos, max_speed=5, acceleration=2, angular_speed=3):
        self.position = list(pos)
        self.speed = 0
        self.theta = angle
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.angular_speed = angular_speed

    def move_forward(self):
        self.speed = min(self.speed + self.acceleration, self.max_speed)

    def move_backward(self):
        self.speed = max(self.speed - self.acceleration, -self.max_speed)

    def rotate(self, left=False, right=False):
        if self.speed != 0:
            if left:
                self.theta += self.angular_speed
            if right:
                self.theta -= self.angular_speed

    def decelerate(self):
        if self.speed > 0:
            self.speed -= 1
        elif self.speed < 0:
            self.speed += 1

    def update_position(self):
        self.decelerate()
        self.position[1] -= self.speed * cos(radians(self.theta))
        self.position[0] -= self.speed * sin(radians(self.theta))

    def bounce(self, multiplier=-1.5):
        self.speed *= multiplier  # Reverse and possibly amplify the speed
        self.position[1] -= self.speed * cos(radians(self.theta))
        self.position[0] -= self.speed * sin(radians(self.theta))
        self.decelerate()

    def get_state(self):
        return {
            "x": self.position[0],
            "y": self.position[1],
            "theta": self.theta,
            "speed": self.speed,
        }

    def set_state(self, state):
        self.position = [state['x'], state['y']]
        self.theta = state['theta']
        self.speed = state['speed']

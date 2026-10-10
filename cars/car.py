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
        # Snapshot position before moving so rollback_position() can restore it
        self._prev_position = list(self.position)
        self.decelerate()
        self.position[1] -= self.speed * cos(radians(self.theta))
        self.position[0] -= self.speed * sin(radians(self.theta))

    def rollback_position(self):
        """Undo the last movement step and stop the car.

        Called when a collision is detected after update_position().
        Restoring to the pre-move coordinate guarantees the car is never
        inside the border mask, which prevents the speed-compounding
        oscillation that bounce() caused:
          bounce(-2): speed flips sign each frame (neg×neg=pos) → grows unboundedly.
        """
        if hasattr(self, '_prev_position'):
            self.position = list(self._prev_position)
        self.speed = 0

    def bounce(self, multiplier=-1.5):
        """Legacy reversal — kept for compatibility. Prefer rollback_position()
        for wall collisions as it cannot compound across frames."""
        self.speed *= multiplier
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
    def get_direction(self):
    # If the car isn't moving, it has no direction. Return a zero vector.
        if self.speed == 0:
            return (0, 0)
        
        # If the car is moving, the original calculation is safe.
        direction_sign = self.speed / abs(self.speed)
        dir_x = direction_sign * sin(radians(self.theta))
        dir_y = direction_sign * -cos(radians(self.theta))
        return (dir_x, dir_y)


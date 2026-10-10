from cars.car import Car
from math import sin, cos, radians, sqrt
import math

# How close (in pixels) the AI needs to be to a waypoint to advance to the next one.
# A rect-collidepoint check was used before, which required a pixel-perfect hit and
# caused the car to overshoot and never advance. Distance threshold is much more reliable.
WAYPOINT_REACH_RADIUS = 20


class AICar(Car):
    def __init__(self, angle, pos, waypoints):
        super().__init__(angle, pos)
        self.path = waypoints
        self.current_point = 0
        self.max_speed = 2

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

    def update_path_point(self):
        # Loop back to the first waypoint so the AI keeps racing indefinitely
        self.current_point = (self.current_point + 1) % len(self.path)

    def _distance_to_current_waypoint(self):
        """Euclidean distance from the car's position to the current target waypoint."""
        tx, ty = self.path[self.current_point]
        dx = tx - self.position[0]
        dy = ty - self.position[1]
        return sqrt(dx * dx + dy * dy)

    def bounce(self, multiplier=-1.5):
        """Override the base bounce so the AI doesn't oscillate against walls.

        The base Car.bounce() multiplies speed by a negative value. When the car
        is still overlapping the border on the next frame it bounces again —
        negative × negative = positive — causing the speed to grow each frame and
        the car to teleport wildly. For the AI, simply zeroing the speed and
        nudging it backward is enough to escape the wall.
        """
        self.speed = 0
        # Nudge backward so the car exits the border area cleanly
        self.position[1] += 2 * cos(radians(self.theta))
        self.position[0] += 2 * sin(radians(self.theta))

    def aimove(self):
        """Steer toward the current waypoint and advance when close enough.

        Waypoint advancement is handled here (distance-based) rather than in the
        game loop to keep navigation logic self-contained in the car class.
        """
        if not self.path:
            return

        # Advance to next waypoint when within reach radius
        if self._distance_to_current_waypoint() < WAYPOINT_REACH_RADIUS:
            self.update_path_point()

        self.calculate_angle()
        self.move_forward()
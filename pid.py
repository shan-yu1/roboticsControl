#!/usr/bin/env python


class PID:
    """
    A PID controller sporting an option to do accumulator min/max anti-windup.
    """

    def __init__(self, Kp=1.0, Ki=0.0, Kd=0.0, reference=None):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.reference = reference
        self.previous_error = 0.0
        self.accumulated_error = 0.0
        self.anti_windup = False

    def control(self, input, reference=None):
        """
        Compute a control value for @input. If no @reference is used, fall
        back to self.reference.
        """
        # Calculate new error and accumulate
        error = (reference if reference else self.reference) - input
        self.accumulated_error += error
        # Check for accumulator limits
        if (self.anti_windup):
            if self.accumulated_error < self.accumulator_min:
                self.accumulated_error = self.accumulator_min
            elif self.accumulated_error > self.accumulator_max:
                self.accumulated_error = self.accumulated_max
        # Calculate control output
        P_term = self.Kp * self.error
        D_term = self.Kd * (error - self.previous_error)
        I_term = self.Ki * self.accumulated_error
        control = P_term + I_term + D_term
        # Store current error
        self.previous_error = error
        # Return control value
        return control

    def anti_windup(self, acc_min, acc_max=None):
        """
        @acc_min false for disabling
        @acc_max defaults to -@acc_min
        """
        self.anti_windup = True if acc_min is not False else False
        self.accumulator_min = acc_min
        self.accumulator_max = acc_max if acc_max is not None else -acc_min


if __name__ == "__main__":
    from math import *

    class robot:
        """
        This is the robot class from Udacity
        """

        def __init__(self, length = 20.0):
            """
            creates robot and initializes location/orientation to 0, 0, 0
            """
            self.x = 0.0
            self.y = 0.0
            self.orientation = 0.0
            self.length = length
            self.steering_noise = 0.0
            self.distance_noise = 0.0
            self.steering_drift = 0.0

        def set(self, new_x, new_y, new_orientation):
            """
            sets a robot coordinate
            """
            self.x = float(new_x)
            self.y = float(new_y)
            self.orientation = float(new_orientation) % (2.0 * pi)

        def set_noise(self, new_s_noise, new_d_noise):
            """
            sets the noise parameters
            makes it possible to change the noise parameters
            this is often useful in particle filters
            """
            self.steering_noise = float(new_s_noise)
            self.distance_noise = float(new_d_noise)

        def set_steering_drift(self, drift):
            """
            sets the systematical steering drift parameter
            """
            self.steering_drift = drift

        def move(self, steering, distance,
                 tolerance=0.001, max_steering_angle=pi/4.0):
            """
            steering = front wheel steering angle, limited by max_steering_angle
            distance = total distance driven, most be non-negative
            """
            if steering > max_steering_angle:
                steering = max_steering_angle
            if steering < -max_steering_angle:
                steering = -max_steering_angle
            if distance < 0.0:
                distance = 0.0

            # make a new copy
            res = robot()
            res.length = self.length
            res.steering_noise = self.steering_noise
            res.distance_noise = self.distance_noise
            res.steering_drift = self.steering_drift

            # apply noise
            steering2 = random.gauss(steering, self.steering_noise)
            distance2 = random.gauss(distance, self.distance_noise)

            # apply steering drift
            steering2 += self.steering_drift

            # Execute motion
            turn = tan(steering2) * distance2 / res.length

            if abs(turn) < tolerance:
                # approximate by straight line motion
                res.x = self.x + (distance2 * cos(self.orientation))
                res.y = self.y + (distance2 * sin(self.orientation))
                res.orientation = (self.orientation + turn) % (2.0 * pi)
            else:
                # approximate bicycle model for motion
                radius = distance2 / turn
                cx = self.x - (sin(self.orientation) * radius)
                cy = self.y + (cos(self.orientation) * radius)
                res.orientation = (self.orientation + turn) % (2.0 * pi)
                res.x = cx + (sin(res.orientation) * radius)
                res.y = cy - (cos(res.orientation) * radius)

            return res

        def __repr__(self):
            return '[x=%.5f y=%.5f orient=%.5f]' % (self.x, self.y, self.orientation)

import time

class PID:

        def __init__(self, P=0.0, I=0.0, D=0.0):

                self.Kp = P
                self.Ki = I
                self.Kd = D

                self.sample_time = 0.01
                self.current_time = time.time()
                self.last_time = self.current_time
                self.delta_time = self.current_time - self.last_time

                self.set_point = 0.0

                self.PTerm = 0.0
                self.ITerm = 0.0
                self.DTerm = 0.0

                self.error = 0.0
                self.last_error = 0.0
                self.delta_error = self.error - self.last_error

#               self.feedback_val = 0.0
                self.output = 0.0

        def set_gains(self, P, I, D):

                self.Kp = P
                self.Ki = I
                self.Kd = D

        def update_pid(self, feedback_val):

                self.error = self.set_point - feedback_val

                self.current_time = time.time()
                self.delta_time = self.current_time - self.last_time
                self.delta_error = self.error - self.last_error

                if (self.delta_time >= self.sample_time):

                        self.PTerm = self.Kp * self.error
                        self.ITerm += self.error * self.delta_time
                        self.DTerm = self.delta_error / self.delta_time

                        self.last_time = self.current_time
                        self.last_error = self.error

                        self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)

        def sample_time(self, sample_time):

                self.sample_time = sample_time

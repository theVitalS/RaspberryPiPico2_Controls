from machine import Pin, PWM

class MotorController:
    def __init__(self, detailed_control=True, debug=False):
        self.debug = debug
        self.detailed_control = detailed_control

        # Motor direction pins
        self.rf = Pin(4, Pin.OUT)
        self.rb = Pin(5, Pin.OUT)
        self.lf = Pin(6, Pin.OUT)
        self.lb = Pin(7, Pin.OUT)

        # Speed control pins (PWM)
        self.ENA = PWM(Pin(3))  # Right motor
        self.ENB = PWM(Pin(8))  # Left motor

        self.ENA.freq(1000)
        self.ENB.freq(1000)

        # Speed control parameters
        self.base_speed = 80
        self.drag_factor = 0
        self.turning_slowdown = 2

    def stop(self):
        self.lf.low()
        self.lb.low()
        self.rf.low()
        self.rb.low()

    def set_speed(self, speed):
        """
        Sets speed on both motors equally.
        """
        duty_right = int(speed * (1 + self.drag_factor) * 65535 / 100)
        duty_left = int(speed * (1 - self.drag_factor) * 65535 / 100)
        self.ENA.duty_u16(min(duty_right, 65535))
        self.ENB.duty_u16(min(duty_left, 65535))

        if self.debug:
            print(f"[Speed] Left: {duty_left}, Right: {duty_right}")

    def set_right_speed(self, speed):
        duty = self._scale_speed(speed)
        self.ENA.duty_u16(duty)
        if self.debug:
            print(f"[Right Speed] Duty: {duty}")

    def set_left_speed(self, speed):
        duty = self._scale_speed(speed)
        self.ENB.duty_u16(duty)
        if self.debug:
            print(f"[Left Speed] Duty: {duty}")

    def _scale_speed(self, speed):
        speed = abs(speed)
        res = (speed * self.base_speed) / 100
        return int(min(res, 100) * 65535 / 100)

    # Directional control
    def left_forward(self): self.lb.low(); self.lf.high()
    def left_backward(self): self.lf.low(); self.lb.high()
    def right_forward(self): self.rb.low(); self.rf.high()
    def right_backward(self): self.rf.low(); self.rb.high()

    def move_forward(self):
        if self.debug:
            print("[Move] Forward")
        self.left_forward()
        self.right_forward()

    def move_backward(self):
        if self.debug:
            print("[Move] Backward")
        self.left_backward()
        self.right_backward()

    def turn_left(self):
        if self.debug:
            print("[Turn] Left")
        self.left_backward()
        self.right_forward()

    def turn_right(self):
        if self.debug:
            print("[Turn] Right")
        self.left_forward()
        self.right_backward()

    def move(self, x, y):
        """
        Interprets joystick x/y to move motors accordingly.
        """
        if not self.detailed_control:
            if x < 50:
                self.turn_left()
            elif x > 50:
                self.turn_right()
            elif y > 50:
                self.move_forward()
            elif y < 50:
                self.move_backward()
            else:
                self.stop()
        else:
            # Scale x/y from 0–100 to -50 to +50
            y -= 50
            x -= 50
            left_vector = y + x
            right_vector = y - x

            self.set_left_speed(left_vector * 2)
            self.set_right_speed(right_vector * 2)

            self.stop()

            if left_vector > 0:
                self.left_forward()
            elif left_vector < 0:
                self.left_backward()

            if right_vector > 0:
                self.right_forward()
            elif right_vector < 0:
                self.right_backward()


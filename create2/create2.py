# coding: UTF-8
'''
Created on 2015/05/18
@author: hosoai
ライブラリのメインクラス．主にこのクラスから操作を行う．
コンストラクタでシリアル・インタフェースの指定とSensorObserverの使用の有無，使用する場合はインターバルを指定する．
'''
import struct
import time

from sensor import Sensor
from opcode import Opcode
from opcode import Modes
from sensor_observer import SensorObserver
from sci import SerialCommandInterface

# create2 tuning parameters
BAUDRATE = 115200
SERIAL_TIMEOUT  = 2

class Create2:
    def __init__(self, tty="/dev/ttyUSB0", threading=False, interval=500):
        time.sleep(2)
        self.sci = SerialCommandInterface(tty, baudrate=BAUDRATE, timeout=SERIAL_TIMEOUT)
        self.opcode = Opcode(self.sci)
        if threading:
            self.observer = SensorObserver(self.sci, interval)
            self.observer.start()
        self.opcode.start()
        self.opcode.safe()
        time.sleep(1)
    
    def start(self):
        self.opcode.start
    def stop(self):
        self.opcode.stop

    def set_mode(self, modes):
        if(modes==Modes.Safe):
            self.opcode.safe
        elif(modes==Modes.Full):
            self.opcode.full
        elif(modes==Modes.Passive):
            self.opcode.start
        elif(modes==Modes.OFF):
            self.power
        
    def drive(self, velocity, radius):
        velocity = int(velocity) & 0xffff
        radius = int(radius) & 0xffff
        data = struct.unpack('4B', struct.pack('>2H', velocity, radius))
        self.opcode.drive(data)
    
    # left and right : wheel velocity(-500 - 500ms/s)
    def drive_wheels(self, left, right):
        args = struct.unpack('4B', struct.pack('>2H', right, left))
        self.opcode.driveWheels(args)
    
    # left and right : motor PWM (-255 - 255)
    def drive_pwm(self, left, right):
        args = struct.unpack('4B', struct.pack('>2H', right, left))
        self.opcode.drivePwm(args)
        
    def brush(self, mainBrush, vacuum, sideBrush):
        self.opcode.motors( (mainBrush << 2 | vacuum<<1 | sideBrush) )
        
    # mainBrushPWM and sideBrushPWM : PWM (-127 - 127)
    # vacuumPWM : PWM (0 - 127)
    def brush_pwm(self, mainBrushPWM, vacuumPWM, sideBrushPWM):
        self.opcode.pwmMotors( [mainBrushPWM, vacuumPWM, sideBrushPWM] )
    
    def docking(self):
        self.opcode.forceSeekingDock
    
    # args : ascii code
    def digit_leds_ascii(self, digit3ascii, digit2ascii, digit1ascii, digit0ascii):
        self.opcode.digitLedsAscii([digit3ascii, digit2ascii, digit1ascii, digit0ascii])

    def request_sensor(self, packetID, numBytes):
        self.sci.flash_input()
        requestBytes = [142, packetID]
        self.sci.send(requestBytes);
        data = self.sci.read(numBytes)
        return data
        
    def request_all_sensor(self):
        self.sci.flash_input()
        requestBytes = [142, 100]
        self.sci.send(requestBytes)
        data = self.sci.read(80)
        return Sensor.gen_from_bytes(data)

# for multithread
    def get_distance(self):
        return self.observer.get_distance()
    def get_angle(self):
        return self.observer.get_angle()
    
    def get_left_encoder(self):
        return self.observer.get_left_encoder()
    
    def get_right_encoder(self):
        return self.observer.get_right_encoder()
    
    def get_sensor(self):
        return self.observer.get_sensor()
    
    def get_sensor_raw(self):
        return self.observer.get_raw_sensor()

    def add_event_listener(self, listener):
        self.observer.add_listener(listener)
    def set_next_distance(self, distance, greater):
        self.observer.set_next_distance(distance, greater)
    def set_next_angle(self, angle, greater):
        self.observer.set_next_angle(angle, greater)

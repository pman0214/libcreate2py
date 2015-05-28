'''
Created on 2015/05/18

@author: hosoai
'''
from threading import Thread
from time import sleep
from create2.sensor import Sensor, PACKET_LENGTH

class SensorObserver(Thread):
    def __init__(self, sci, interval):
        super(SensorObserver, self).__init__()
        self.sci = sci
        self.interval = interval
        self.running = True
        self.prevSensor = Sensor()
        self.listeners = []

    def addListener(self, listener):
        self.listeners.append(listener)

    def stop(self):
        self.running = False

    def getSensor(self):
        return self.sensor

    def getRawSensor(self):
        return self.data

    def requestSensor(self):
        self.sci.FlushInput()
        requestBytes = [142, 100]
        self.sci.Send(requestBytes)

    def raiseEvent(self, eventList):
        print "Raise Event"
        for listener in self.listeners:
            listener(eventList)

    def run(self):
        while(self.running):
            self.requestSensor()
            self.data = self.sci.Read(PACKET_LENGTH)
            self.sensor = Sensor.genFromBytes(self.data)
            if self.prevSensor != None:
                eventList = self.sensor.diff(self.prevSensor)
                if (eventList != None and len(eventList)>0):
                    self.raiseEvent(eventList)
            self.prevSensor = self.sensor
            sleep(self.interval)

# test
#observer = SensorObserver(serial.Serial("COM6", baudrate=115200, timeout=2), 1)
#observer.start()

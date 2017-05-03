from pyflirpt.utils import ptlogger
from pyflirpt.keyboard import keyboard
import os
import sys
import time
from itertools import cycle

CONFIG_FILE = "movement.conf"

class UOIR(object):

    def __init__(self):
        self.logger = ptlogger.ptlogger(tofile=True)
        self.keycontrol = self.getKeyObj()
        
    def getKeyObj(self):
        try:
            keycontrol = keyboard.KeyboardController(pt_ip="192.168.1.50",
                                                     pt_port=4000)
            self.logger.info("Got PT")
            return keycontrol
        except Exception as ex:
            self.critical("Cannot get keycontrol object: "+str(ex))
            sys.exit(1)
            
    def initialize(self):
        positions = []
        with open(CONFIG_FILE, 'r') as c_handler:
            positions = c_handler.readlines()
            self.logger.info("Total positions: " + str(len(positions) + 1))
        return positions

    def runTask(self, pos_cycle):
        while True:
            try:
                print("Here")
                # Create an iterator cycle for the positions
                position = pos_cycle.next()
                self.logger.info("Moving to position: " + str(position))
                self.pan_pos = position.split('_')[0]
                self.tilt_pos = position.split('_')[1].split(',')[0]
            
                # ---- Hacky way to remove p and n from pan and tilt
                # and replace them with + / - signs
                if "p" in self.pan_pos:
                    self.pan_pos = self.pan_pos.strip("p")
                elif "n" in self.pan_pos:
                    self.pan_pos = "-"+self.pan_pos.strip("n")
                if "p" in self.tilt_pos:
                    self.tilt_pos = self.tilt_pos.strip("p")
                elif "n" in self.tilt_pos:
                    self.tilt_pos = "-"+self.tilt_pos.strip("n")
                # ----
        
                self.zoom_fac = position.split(',')[1]
                self.keycontrol.pan(self.pan_pos)
                self.keycontrol.tilt(self.tilt_pos)
                
                while not self.keycontrol.ready():
                    self.logger.info("Waiting for PT module ")
            
            except Exception as ex:
                self.logger.critical("RunTask exception: "+str(ex))
                sys.exit(1)
                
        time.sleep(1)

if __name__ == "__main__":
    uoir = UOIR()
    positions = uoir.initialize()
    position_cycle = cycle(positions)
    uoir.runTask(position_cycle)

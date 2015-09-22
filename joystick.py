"""
Python Controller for Pan and Tilt
Author: Mohit Sharma
Version: Development
"""
import pygame
import os
import sys
import signal
import subprocess
from collections import OrderedDict
import time
from blessings import Terminal


# Boolean for Auth
_is_authentic = False
# Message if not Authenticated
_non_auth_message='''                                                                                                                                                                                 
        *****************************************************
        Authentication Failed. You are either:
        - Not authorized to control the Joystick.
        - Didn't call the auth() method to get authenticated.
        ***************************************************** 
        '''

def authenticate(func):
    def _auth_and_call(*args, **kwargs):
        if not _is_authentic:
            print 'Auth Failed'
            raise Exception(_non_auth_message)
        return func(*args, **kwargs)
    return _auth_and_call

class JoystickControl(object):
    """
    Class containing the methods 
    to control the pan and tilt using
    compatible joysticks
    """
    def __init__(self):
        self._is_authentic = _is_authentic
        self.term = Terminal()
        self._ok = self.term.green_bold('[PyFlirPT]:')
        pygame.init()
        
    def auth(self):
        p = subprocess.Popen(['gksudo', 'echo "Authenticated"'],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        print out, err
        if out:
            global _is_authentic
            _is_authentic = True
            print 'Auth Successful.'
        else:
            raise Exception(_non_auth_message)

    def exit_gracefully(self, signum, frame):
        signal.signal(signal.SIGINT, signal.getsignal(signal.SIGINT))
        try:
            if raw_input('Exit? (y / n) > ').lower().startswith('y'):
                sys.exit(1)
        except KeyboardInterrupt:
            print 'OK, OK Quitting...'
            sys.exit()
            
    def list_joysticks(self):
        joysticks = pygame.joystick.get_count()
        for ids in range(joysticks):
            joystick = pygame.joystick.Joystick(ids)
            joystick.init()
            print self._ok, ids, ':', joystick.get_name(), '\n'
        print '-'*20

    def _initialize(self, ids):
        """
        Initialize the joystick id passed as ids parameter.
        Get information on all the joystick control and
        create a dictionary which will be used for control.
        """
        joystick = pygame.joystick.Joystick(ids)
        joystick.init()
        self.axes = ['axis_%d'%a for a in range(joystick.get_numaxes())]
        self.buttons = ['button_%d'%b for b in range(joystick.get_numbuttons())]
        self.hats = ['hat_%d'%h for h in range(joystick.get_numhats())]

        self.d = {}
        self.d = OrderedDict.fromkeys(self.buttons)
        self.d.update(OrderedDict.fromkeys(self.hats))
        self.d.update(OrderedDict.fromkeys(self.buttons))

        return joystick

    def _move(self, axis, posn):
        print 'axis', axis
        print 'posn', posn
        
        #p = subprocess.Popen(['ssh', '128.122.72.97',
        #                      'echo -ne "PP%d \n TP%d \n" |  nc 192.168.1.50 4000'%(
        #                          int(joystick.get_axis(0)*4000),
        #                          int(joystick.get_axis(1)*4000))],
        #                     stdout=subprocess.PIPE)

        #out, err = p.communicate()
        #print out.split('\r')[5:]
        
    def select_joystick(self, ids):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        # ToDo: Better way to store all controls in dictionary
        # that is defined in initialized method

        joystick = self._initialize(ids)
        #self.d = self._initialize(ids)
        while 1:
            pygame.event.get()
            for i in range(joystick.get_numaxes()):
                if joystick.get_axis(i):
                    self._move(i, joystick.get_axis(i)*4000)

                if joystick.get_button(i):
                    self._move(i, joystick.get_button(i))    
                
            #p = subprocess.Popen(['ssh', '128.122.72.97',
            #                      'echo -ne "PP%d \n TP%d \n" |  nc 192.168.1.50 4000'%(
            #                          int(joystick.get_axis(0)*4000),
            #                          int(joystick.get_axis(1)*4000))],
            #                     stdout=subprocess.PIPE)
            
            #out, err = p.communicate()
            #print out.split('\r')[5:]
            time.sleep(.2)
        
if __name__ == '__main__':
    jc = JoystickControl()
    jc.list_joysticks()

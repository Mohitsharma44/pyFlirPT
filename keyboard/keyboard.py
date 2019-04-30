# -* coding: utf-8 -*-
# Author : Mohit Sharma
# June 08 2016
# NYU CUSP 2016

import telnetlib
import atexit
import sys
import ast
import time
import logging
import socket
from telnetlib import IAC, NOP
from pyflirpt.utils import ptlogger
import traceback

class KeyboardController(object):
    """
    Class containing methods to control the
    FLIR E series pan and tilt using the Keyboard
    """
    def __init__(self, pt_ip, pt_port):
        self.logger = ptlogger.ptlogger(tofile=True)
        self.PT_IP = pt_ip
        self.PT_PORT = pt_port
        self.cursor = b"*"
        self.sentinel = b"\r\n"
        # Max Pan and Tilt allowed
        self.PPmax = 4000
        self.PPmin = -4000
        self.TPmax = 2100
        self.TPmin = -2100
        # Max Pan and Tilt speed
        self.PSmax = 2000
        self.TSmax = 2000
        self.tn = self._openTelnet(self.PT_IP, self.PT_PORT)
        atexit.register(self.cleanup)
        self.resetPT()

    def _openTelnet(self, host, port):
        """                                                                                                                                                                                                 
        Open Telnet connection with the host                                                                                                                                                                
        Parameters                                                                                                                                                                                          
        ----------                                                                                                                                                                                          
        host : str                                                                                                                                                                                          
            ip address of the host to connect to                                                                                                                                                            
        port : int                                                                                                                                                                                          
            port number to connect to                                                                                                                                                                      
                                                                                                                                                                                                            
        Returns                                                                                                                                                                                             
        -------                                                                                                                                                                                             
        tn : telnet object                                                                                                                                                                                  
        """
        self.logger.info("Opening Telnet connection")
        tn = telnetlib.Telnet()
        tn.open(host, port)
        self.logger.debug(tn.read_until(self.cursor+self.sentinel))
        # Keep Telnet socket Alive!
        self._keepConnectionAlive(tn.sock)
        return tn

    def _closeTelnet(self, tn=None):
        """                                                                                                                                                                                                 
        Close the telnet connection.                                                                                                                                                                        
                                                                                                                                                                                                            
        Parameters                                                                                                                                                                                          
        ----------                                                                                                                                                                                          
        tn: Telnet object                                                                                                                                                                                   
            Optional. If not passes, it will close the                                                                                                                                                      
            existing telnet connection                                                                                                                                                                     
                                                                                                                                                                                                            
        """
        try:
            self.logger.warning("Closing Telnet connection")
            tn = tn if tn else self.tn
            tn.write(b'\x1d'+self.sentinel)
            tn.close()
        except Exception as ex:
            self.logger.error("Error closing telnet: "+str(ex))

    def _keepConnectionAlive(self, sock, idle_after_sec=1, interval_sec=3, max_fails=5):
        """
        Keep the socket alive                                                  

        Parameters                                                             
        ----------                                                                     
        sock: TCP socket                                                               
        idle_after_sec: int                                                                
            activate after `idle_after` seconds of idleness                                
            default: 1                                                                 
        interval_sec: int                                                                  
            interval between which keepalive ping is to be sent                            
            default: 3                                                                 
        max_fails: int                                                                     
            maximum keep alive attempts before closing the socket                          
            default: 5                                                                                                                                                """
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, idle_after_sec)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)
        
    def _checkTelnetConnection(self, tnsock=None):
        """                                                                            
        Check the telnet connection is alive or not                            

        Parameters                                                                     
        ----------                                                                     
        tnsock: Telnet socket                                                  

        Returns           
        -------                                                                        
        True: bool                                                                          
        if the connection is alive                                                
        """
        try:
            tnsock.sendall(IAC + NOP)
            self.logger.debug("Detected Telnet connection is alive")
            return True
        except Exception:
            self.logger.warning("Detected Telnet connection is dead")
            return False


    def _resetTelnetConnection(self, tn=None):
        """                                                                    
        Close the Telnet connection and
        Reopen them                                                            

        Parameters                                                                     
        ----------                                                                     
        tn: Telnet object                                                                  
            Optional. If not passed, it will close and reopen                              
            the existing telnet connection                                             
            ..Note: This will make all the old telnet objects point                             
            to the new object                                                         
        """
        self.logger.warning("Restarting Telnet connection")
        self._closeTelnet(tn)
        self.tn = None
        time.sleep(1)
        self.tn = self._openTelnet(self.PT_IP, self.PT_PORT)
        
    def execute(self, command):
        """
        Execute the telnet command on the device
        by performing appropriate addition of sentinels
        and padding

        Parameters:
        -----------
        command : str
            command to be executed on the pan and tilt

        Returns:
        --------
        output : str
            formatted reply of the executed command
        """
        try:
            self.logger.debug("Executing: "+str(command))
            self.tn.write(command+self.sentinel)
            output = self.tn.read_until(self.sentinel)
            self.logger.debug("Reply    : %s "%output)
            return output
        except IOError as io:
            # restart PT
            self._resetTelnetConnection(self.tn)
            self.execute(command)
        except Exception as ex:
            self.logger.error("Exception: "+str(ex))
            
            
    def ready(self):
        """
        Returns whether the pan and tilt
        has finished executing previous pan or tilt command
        Returns:
        ready : bool
            True if the module is ready
        """

        command = b"B"
        output = self.execute(command)
        if output.strip().split()[2] == b'S(0,0)':
            return True
        else:
            return False

    def current_pos(self):
        """
        Returns current pan and tilt position as a tuple
        (pan, tilt)
        """
        command = b"B"
        output = self.execute(command)
        return ast.literal_eval(output.strip().split()[1].decode("ascii").strip('P'))
        
    def resetPT(self):
        """
        Method to reset the pan and tilt's speed
        """
        commands = [b'ED', b'CI', b'PS150', b'TS150', b'LU']
        map(lambda x: self.execute(x), commands)

    def pan(self, posn):
        """
        Method to pan the camera between the restricted
        absolute positions `PPmin` and `PPmax`
        
        Paramters:
        ----------
        posn : str
            absolute position to pan the camera at

        Returns:
        --------
        None
        """
        if self.PPmin <= int(posn) <= self.PPmax:
            command = b"PP"+str(posn).encode()
            self.execute(command)
        else:
            self.logger.warning("Cannot go beyond Limits ")

    def tilt(self, posn):
        """
        Method to tilt the camera between the restricted
        absolute positions `TPmin` and `TPmax`
        
        Paramters:
        ----------
        posn : str
            absolute position to tilt the camera at

        Returns:
        --------
        None
        """
        if self.TPmin <= int(posn) <= self.TPmax:
            command = b"TP"+str(posn).encode()
            self.execute(command)
        else:
            self.logger.warning("Cannot go beyond Limits ")

    def cleanup(self):
        """
        Make sure to close the telnet connection and curses window
        before exiting the program
        """
        self.logger.info("Quitting Control ")
        self._closeTelnet(self.tn)
        traceback.print_exc()

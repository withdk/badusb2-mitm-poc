#!/usr/bin/env python

#GoodFET MAXIM MAX3421 and MAX3420 Client
#by Travis Goodspeed
#
# BadUSB 2.0 by DK 2016 (@withdk)
#

import sys;
import binascii;
import array;
import warnings;
import signal;

from GoodFETMAXUSB import GoodFETMAXUSBHID;

def signal_handler(signal, frame):
  print('Exiting host...')
  client.usb_disconnect()
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler);
 
#Initialize FET and set baud rate
client=GoodFETMAXUSBHID();
client.serInit();


client.MAXUSBsetup();
client.hidinit();


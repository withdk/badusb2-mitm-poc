#!/usr/bin/env python

# BadUSB 2.0 by DK 2016 (@withdk)

import os;
import sys;
import binascii;
import array;
import time;
import warnings;
import signal;

rHCTL=29
bmBUSRST=0x01

from GoodFETMAXUSB import GoodFETMAXUSBHost;
rcv_h2p_ep0="";


def signal_handler(signal, frame):
  print('Exiting host...')
  client.usb_disconnect()
  sys.exit(0)

read_h2p_ep0 = "/tmp/write_h2p_ep0"
write_p2h_ep0 = "/tmp/write_p2h_ep0"
read_h2p_ep3 = "/tmp/write_h2p_ep3"
write_p2h_ep3 = "/tmp/write_p2h_ep3"
        
try:
    os.mkfifo(read_h2p_ep0)
    os.mkfifo(write_p2h_ep0)
    os.mkfifo(read_h2p_ep3)
    os.mkfifo(write_p2h_ep3)
except OSError:
    pass

print "Ensure the Facedancer connected to the peripheral was plugged in first and registered on /dev/ttyUSB0"
print ""
signal.signal(signal.SIGINT, signal_handler)
#Initialize FET and set baud rate
client=GoodFETMAXUSBHost();
client.serInit()
client.MAXUSBsetup();
client.hostrun();
client.wait_for_disconnect();

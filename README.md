$ ./badusb2.py 

 ******                  ** **     **  ******** ******          ****      **** 
/*////**                /**/**    /** **////// /*////**        */// *    *///**
/*   /**   ******       /**/**    /**/**       /*   /**       /    /*   /*  */*
/******   //////**   ******/**    /**/*********/******           ***    /* * /*
/*//// **  *******  **///**/**    /**////////**/*//// **        *//     /**  /*
/*    /** **////** /**  /**/**    /**       /**/*    /**       *      **/*   /*
/******* //********//******//*******  ******** /*******       /******/**/ **** 
///////   ////////  //////  ///////  ////////  ///////        ////// //  ////

	- BadUSB 2.0 USB MITM POC


BadUSB 2$ help

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

BadUSB 2$ What should we do today?

Introduction - a bit wordy, pasted from my original paper

The advanced uses and capabilities of rogue USB hardware implants for use in cyber espionage activities is still very much an unknown quantity in the industry. Security professionals are in considerable need of tools capable of exploring the threat landscape, and generating awareness in this area. BadUSB2, is a tool capable of compromising USB fixed-line communications through an active man-in-the-middle attack. It is able to achieve the same results as hardware keyloggers, keyboard emulation, and BadUSB hardware implants. Furthermore, BadUSB2 introduces new techniques to defeat keyboard-based one-time-password systems, automatically replay user credentials, as well as acquiring an interactive command shell over USB. 

But we already have Rubber ducky!

So how is this any different from existing USB hardware implants like the Rubber Ducky, or keyloggers. Firstly, the devices I've seen can only achieve one or two attack classes such as eavesdropping or message fabrication. BadUSB2 can eavesdrop, replay, modify, fabricate, exfiltrate data and BadUSB in one device. Furthermore, when combining these attack classes really interesting attack scenarios begin to surface. Secondly, keyboard emulation devices register as an additional USB device making them easy to detect and block, i.e. why do I now have two keyboards attached!? Yes, such devices can be easily detected and blocked. The same can be said of BadUSB, it often needs to register as a secondary USB device to perform a malicious task. BadUSB2 is an INLINE hardware implant giving it the stealth of a hardware keylogger but far more capabilities as mentioned above. Finally, (law of 3's), just cos...

Implemented Proof of Concept Attacks

Eavesdrop. Once the keyboard has been registered to the target all keystrokes are captured to the '/tmp' folder.

Modify. Weaponised code could use regular expressions to modify user keystrokes in order to defeat one-time-passwords. In this POC we simply annoy the user :)

Replay. The POC code will automatically detect 'ctrl-alt-delete' and assume it is a login session. It stops recording once the 'enter' key is pressed. Ay any time the 'replay' command can be given to automatically authenticate to the workstation.

Fabricate. Start/Run or generic commands can be issued to the target operating-system just as if you were at the keyboard. 

Exfiltrate. I've implemented a PowerShell exfiltration POC that uses the 'morse code' technique (LEDs) to exfiltrate data. Using custom HID output reports is faster but MS Windows restricts read/write access from Win 2K. In short, this is a very rudimentary POC, and did I mention very slow! 

BadUSB. I did not actually implement a POC for this. The Facedancer has plenty of example code that can be used to fake USB peripherals to the host, but it would be nice to implement some of the BadUSB "Kali Nethunter" type attacks here.

Conclusion:

Yes the 'risk assessment' will say this is a low risk because you need physical access. Maybe so, but I'd keep in mind that a weaponised version of this design would likely utilise some form of RF, so getting access once may be enough to persist an attack. Also, when was the last time you tested hardware delivered by your suppliers!? Supply chain attacks are real - Just saying :)
 
With BadUSB and so many other malicious USB devices, Von Tonder's design could also be used for BadUSB forensics. Looking at traffic over the
 wire and being able to craft responses could be very useful.

Credits

This project builds on the USB-MITM architecture introduced by Rijnard van Tonder and Herman Engelbrecht in their paper titled, "Lowering the USB Fuzzing Barrier by Transparent Two-Way Emulation". A special thanks to Rijnard for such a brilliant idea.

I have to say thank you to Travis Goodspeed for designing and creating the Facedancer devices and the useful libraries that come with it.

Dominic Spill for his great work in this area and for pointing out Rijnard's project.

Further Information

If you are really bored or just really eager to understand all the ins and outs my original paper can be found on the Royal Holloway ISG website.

I think of all the areas I researched, Adrian Crenshaw's (aka IronGeek) sticks out. He really has spent a lot of his time in building and developing hardware keyloggers and has a plethora of ideas to consider. So for research purposes check his site out.

Disclaimer

This is ALPHA code only!!! If it breaks well don't say I didn't warn you. I have tried to make it somewhat useable with the INSTALL file and building an easy to use menu system, however, keep in mind it is only a proof of concept. 

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

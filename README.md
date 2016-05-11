# badusb2-mitm-poc
BadUSB 2.0 USB-HID MiTM POC

Introduction

The advanced uses and capabilities of rogue USB hardware implants for use in cyber espionage activities is still very much an unknown quantity in the industry. Security professionals are in considerable need of tools capable of exploring the threat landscape, and generating awareness in thisarea. BadUSB2, is a tool capable of compromising USB fixed-line communications through an active man-in-the-middle attack. It is able to achieve the same results as hardware keyloggers, keyboard emulation, and BadUSB hardware implants. Furthermore, BadUSB2 introduces new techniques to defeat keyboard-based one-time-password systems, automatically replay user credentials, as well as acquiring an interactive command shell over USB. 

From my initial conversations with security professionals they tend to ask how this is any different from existing USB hardware implants. BadUSB2 is an all-in-one, inline hardware implant. This means it has the stealth of a hardware keylogger but the capabilities of more sophosticated devices like the Rubber Ducky. 

This project builds on the USB-MITM architecture introduced by Rijnard van Tonder and Herman Engelbrecht in their paper titled, "Lowering the USB Fuzzing Barrier by Transparent Two-Way Emulation". As in Rijnard's paper, the BadUSB2 tool also utilises two 'Facedancer' devices designed by Travis Goodspeed.

I need to sort out 'hacks' for public release but I will aim to release the code in June so other researchers can hopefully benefit and build on this.

Full details of the project are available here:
https://www.royalholloway.ac.uk/isg/documents/pdf/technicalreports/2016/rhul-isg-2016-7-david-kierznowski.pdf



# a module for Klipper to control neopixels with a GPIO directly on the Raspberry Pi

## The alleged challenge

This module was started as a friendly challenge for this sentence in klipper documentation:

> Note that the linux mcu implementation does not currently support directly connected neopixels. The current design using the Linux kernel interface does not allow this scenario because the kernel GPIO interface is not fast enough to provide the required pulse rates." 

[Klipper Config Reference](https://www.klipper3d.org/Config_Reference.html#neopixel)

Things changed after reading the sentence word by word, no doubt, this can't be challenged, its 100% true.

What most people suggested to me, pointing to this sentence, was "Its not possible to control neopixels from klipper on the pi gpio", this is not stated in the sentence above and is wrong.

Why is the sentence correct or the reasons why bitbanging can't work from userland of a modern Operating System:

- Each call needs a context change from userland to kernel and back
Those context changes / calls are anything but cheap, meaning the time to change context and the time needed to verify the parameters.

- bitbanging didnt like unpredictable interruptions
On an Linux your userland process is interuptet when ever the sheduler needs to run a process with higher priorty, also a process that calls the kernel is interupted, a context change is regulary such an interuption.
It is not predictabele how long the interuption takes place.

To solve this problem it is imperative to use dedicated hardware aka DMA.

There are a few ways:

- Write a kernel driver to use the hardware
Needs real knowlege how the kernel works.

- program SPI, PCM (aka I2S), PWM hardware from userland
Urgly to call hardware directly from userland, IMHO a bit risky, it works only when the userland process is run as root for a reason, see warning bellow!.

- Use an existing hardware kernel driver like SPI
Use a Device Driver to control the hardware w/o risk from a user process.

The library used here takes advantage of the last two.

> *WARNING*: 

> _Using the PCM(I2S) or PWM interface of this module is an advanced topic and can result in fatal errors like destroyed filesystems, unusable state after starting klipper, ect. Use only when you know how the resources are used on your pi._

## Current status

- runs with 250 and more pixels.

- Needs testing under heavy load / with more pixels

- Needs more/better documentation.

If it is requested by the community i will do the needed actions to contribute this to the Klipper repository. To avoid waste of time, i will start after the community requst is accepted by an official maintainer.

## Current features

- Supports all stripe types supported by the rpi_ws281x library. 

- Supports the SET_LED multiplexed gcode command.

- Supports a SET_PI_LED (nonmultiplexed) gcode command when enabled that can be run even when status is disconnected (aka. controller error) to signal exceptions via the pixels.

## Planed

(nothing so far)

## Files

|Name|Description|
|:---|:---|
|neo_pi_xel.cfg|Configuration documentation for the extra module|
|neo_pi_xel_pi.py|Python Code|

## Installation

* Enable SPI in kernel (for SPI only) 
  * connect to you pi via ssh
  * run "sudo raspi-conf" (remove the quotes!)
  * navigate to "Interface Options" and select
  * navigart to "SPI" and select
  * select "yes"

* Disable analog audio driver (for PWM only)
See system documentation to disable kernel driver

* Disable digital audio driver (for PCM (aka I2S) only)
See system documentation to disable kernel driver

* Add rpi_ws281x python module to the virtual environment that runs klippy:
  * connect to you pi via ssh
  * change to dirextory /home/pi/klippy_env
  * execute "bin/pip install rpi_ws281x" (remove the quotes!)

* Copy neo_pi_xel.py into your /home/pi/klippy/extras directory

* Add the lines from neo_pi_xel.cfg to your printer.cfg and customize it to your needs.

# Thanks

Special thanks to 

Jeremy Garff (jer@jers.net) (c library, rpi_ws281x python module)

Tony DiCola (tony@tonydicola.com) (rpi_ws281x python module)

Thanks to everyone else who is involved directly or indirectly into making rpi_ws281x library and making this klipper module possible.

# License

Copyright (C) 2022 by Emmo Emminghaus < mo2000 @ mo2000.de >

The code and documentation of this module is provided under the GPLv3 License.

The RPi WS281x Python Module has its own License and Copyright, refer to [RPi WS281x Python on github](https://github.com/rpi-ws281x/rpi-ws281x-python]
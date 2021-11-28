# a simple control module for Klipper to control the chamber temperature in my voron 2.4

**Please use this [Klipper Discourse Thread](https://klipper.discourse.group/t/a-virtual-chamber-heater-extra-python-module/1419) to discus this.**

The idea is not new but i did only find macro based solutions to control the fan:
One or more fans moving air under the heatbed and transfer the heat into the chamber.
(if done properly you can smelt down the plastic parts in you chamber :smiley: )

## Whats the difference to a macro based solution?

Not much...

- It shows up like a real chamber heater, including output of current and target temperature.
This is why this module exists!
- Does wait for the bed to reach its target temperature before starting the fan, to avoid bed heater errors (I had this all the time when i started from cold).
- It needs one simple config section
- No complex startup gcode to heat up, somthing like M140 S100; M191 S50; M109 S240 (or M140 S115; M191 S50; M104 S240; M190 S100; M140 S240 to do it a bit faster/smarter)

## Current status

Does its job, some (anoing) switching the fans a few times  when the bed temperature is almost reached.

## Current features

- Supports M141 (set chamber temperarture) and M191 (set chamber temperarture) gecodes
- Controls temperature while printing w/o infering with the print (less than 1° cooldown of the bed, air is cirulated as slow as possible to hold the temperature).
- Waits for bed reaching its target temperature before the fan is started to avoid heater errors.

## Planed

- Shorten code and remove any unneded/experimental code.
- Give the config section / extra a better name.
- Using the control classes from pheaters (BangBang and PID) to control the fan speed instead of my KISS code.
- Using a compartment fan to cool down the chamber when overheated
- Complete documentation
- Control more fans
- Some checks and failure when temperature can't be reached (e.g. difference chamber / bed temp is below a certain level on M191)

## Files

|Name|Description|
|:---|:---|
|chamber_bedflowheater.cfg|Configuration documentation for the extra|
|chamber_bedflowheater.py|Python Code|

## Installation

Just copy chamber_bedflowheater.py into your klippy/extras directory and add the nessesasy lines from chamber_bedflowheater.cfg to your printer.cfg
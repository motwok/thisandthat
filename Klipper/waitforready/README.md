# a simple module that adds WAITFORREADY gcode command to Klipper

The idea is to wait e. g. after a FIRMWARE_RESTART for the ready state / event.

## Why no macro based solution?

Impossible, the gcode command is registered with WhenNotReady=True so it works when not ready.

## Current status

Done

## Current features

- Supports a WAITFORREADY gcode, when used waits until printer is ready or Timeout is reached (Paramter T or 60 seconds)

## Planed

- Nothing

## Files

|Name|Description|
|:---|:---|
|waitforready.py|Python Code|

## Installation

Just copy waitforready.py into your klippy/extras directory and add a line with "[waitforready}" to your printer.cfg

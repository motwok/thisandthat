# Wifi_now, a ESP_now component for esphome

Add ESP_now functionality to esphome and comunicate directly with other ESP Devices.

This work was already send as PR to esphome and was not reviewed and not accepted after heavy overworking to meet the "coding standards", the PR was maintaineed over 1 year.

Even the small wifi_coop update wasnt accepted. So if you want to use this you have to do the change by yourself.

## Status

It fits **my** needs.

After having my PR canceled after one year, i am not motivated to waste time until i need the changes for my projects, even if listed below.

All changes maintained in this repository, no where else.

## Planed
- Auto channeling, finding devices on other channels.
- Proxydevice, to enable devices only reachable via esp_now to communicate with HA and allow OTA updates.
- Solving the interoperability problem between ESP8266 and ESP32.
- Testing Deep Sleep behaviour/implementation (to use an ESP32 as an remote control for HA)

## Installation
- Neutralize WIFI uncooperative behaviour (disable/reset esp wifi on reconnect all the time disables/resets also esp_now) yust do the changes you can find in [wifi_basic_coop.commit](wifi_basic_coop.commit) to the wifi module.
- Copy folder [wifi_now](wifi_now) to your esphome custom_components folder
- Add wifi now to your yaml, see [wifi_now.rst](wifi_now.rst)

## Documentation

see [wifi_now.rst](wifi_now.rst)

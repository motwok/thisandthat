# Support for "neopixel" leds
#
# Copyright (C) 2022  Emmo Emminghaus <mo2000@mo2000.de>
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# parts from neopixel.py:
#
# Copyright (C) 2019-2022  Kevin O'Connor <kevin@koconnor.net>
#
import logging
from rpi_ws281x import PixelStrip, Color, ws

class PrinterNeo_Pi_Xel:
    def __init__(self, config):
        self.printer = printer = config.get_printer()
        self.mutex = printer.get_reactor().mutex()

        # Configure neopixel

        self.led_count = config.getint('count', 1, minval=1)
        # TODO alle supporteten reinstellen
        led_pins = {
            # PWM0
            12: [12, 0],
            18: [18, 0],
            40: [40, 0],
            52: [52, 0],
            # PWM1
            13: [13, 1],
            19: [19, 1],
            41: [41, 1],
            45: [45, 1], 
            53: [53, 1], 
            #PCM
            21: [21, 0],
            31: [31, 0], 
            #SPI
            10: [10, 0],
            38: [38, 0],
            } 
        self.led_pin, self.led_channel = config.getchoice('pin', led_pins, 10)
        self.led_freq_hz = config.getint('freq_hz', ws.WS2811_TARGET_FREQ, minval=10000)
        self.led_dma = config.getint('dma', 10, minval=8)
        self.led_invert = config.getboolean('invert', False)
        self.led_brightness = config.getint('brightness', 255, minval=0, maxval = 255)
        stripe_types = {
            "SK6812_STRIP_RGBW": [ws.SK6812_STRIP_RGBW, True],
            "SK6812_STRIP_RBGW": [ws.SK6812_STRIP_RGBW, True],
            "SK6812_STRIP_GRBW": [ws.SK6812_STRIP_GRBW, True],
            "SK6812_STRIP_GBRW": [ws.SK6812_STRIP_GBRW, True],
            "SK6812_STRIP_BRGW": [ws.SK6812_STRIP_BRGW, True],
            "SK6812_STRIP_BGRW": [ws.SK6812_STRIP_BGRW, True],
            "WS2811_STRIP_RGB": [ws.WS2811_STRIP_RGB, False],
            "WS2811_STRIP_RBG": [ws.WS2811_STRIP_RBG, False],
            "WS2811_STRIP_GRB": [ws.WS2811_STRIP_GRB, False],
            "WS2811_STRIP_GBR": [ws.WS2811_STRIP_GBR, False],
            "WS2811_STRIP_BRG": [ws.WS2811_STRIP_BRG, False],
            "WS2811_STRIP_BGR": [ws.WS2811_STRIP_BGR, False],
            "WS2812_STRIP": [ws.WS2812_STRIP, False],
            "SK6812_STRIP": [ws.SK6812_STRIP, False],
            "SK6812W_STRIP": [ws.SK6812W_STRIP, True],
            }
        self.stripe_type, self.stripe_haswhite = config.getchoice("type", stripe_types, "WS2812_STRIP")
        enable_set_pi_led = config.getboolean('enable_set_pi_led', False)

        # initialize LED stripe
        self.strip = PixelStrip(self.led_count, self.led_pin, self.led_freq_hz, 
            self.led_dma, self.led_invert, self.led_brightness, self.led_channel, 
            self.stripe_type)
        self.strip.begin()
        
        # Initialize color data
        pled = printer.load_object(config, "led")
        self.led_helper = pled.setup_helper(config, self.update_leds,
                                            self.led_count)
        new_led_state = self.new_led_state = []                                    
        old_led_state = self.old_led_state = []                                    
        new_led_state[:] = self.led_helper.get_status()['color_data']
        old_led_state[:] = new_led_state
                                            
        # Register callbacks
        printer.register_event_handler("klippy:connect", self.send_data)

        # register Commands
        gcode = self.printer.lookup_object('gcode')
        # this is the version or SET_LED that can be calles when MCU is offline!
        if enable_set_pi_led:
            gcode.register_command("SET_PI_LED", self.cmd_SET_LED, True,
                                        desc=self.cmd_SET_LED_help)

            
    def update_color_data(self, led_state):
        new_led_state = self.new_led_state
        new_led_state[:] = led_state
            
    def send_data(self, print_time=None):
        old_led_state = self.old_led_state
        new_led_state = self.new_led_state
        stripe_haswhite = self.stripe_haswhite
        diffs = [[i, n] for i, (n, o) in enumerate(zip(new_led_state, old_led_state))
                 if n != o]
        for pos, newdata in diffs:
            red = int(newdata[0] * 255. + .5)
            green = int(newdata[1] * 255. + .5)
            blue = int(newdata[2] * 255. + .5)
            white = 0
            if stripe_haswhite:
                white = int(newdata[3] * 255. + .5)
            color = Color(red, green, blue, white)
            self.strip.setPixelColor(pos, color)
                 
        old_led_state[:] = new_led_state
        self.strip.show();
                
    def update_leds(self, led_state, print_time):
        def reactor_bgfunc(eventtime):
            with self.mutex:
                self.update_color_data(led_state)
                self.send_data(print_time)
        self.printer.get_reactor().register_callback(reactor_bgfunc)
        
    cmd_SET_LED_help = "Set the color of an LED on raspbery pi"
    def cmd_SET_LED(self, gcmd):
        red = gcmd.get_float('RED', 0., minval=0., maxval=1.)
        green = gcmd.get_float('GREEN', 0., minval=0., maxval=1.)
        blue = gcmd.get_float('BLUE', 0., minval=0., maxval=1.)
        white = gcmd.get_float('WHITE', 0., minval=0., maxval=1.)
        index = gcmd.get_int('INDEX', None, minval=1, maxval=self.led_count)
        transmit = gcmd.get_int('TRANSMIT', 1)
        color = (red, green, blue, white)
        self.led_helper.set_color(index, color)
        if transmit:
            self.led_helper.check_transmit(None)
        
    def get_status(self, eventtime=None):
        return self.led_helper.get_status(eventtime)


def load_config_prefix(config):
    return PrinterNeo_Pi_Xel(config)

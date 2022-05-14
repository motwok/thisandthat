# Support a bed fan regulated chamber temperature
#
# Copyright (C) 2021  Emmo Emminghaus <mo2000@mo2000.de>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import threading
from . import fan

KELVIN_TO_CELSIUS = -273.15
PIN_MIN_TIME = 0.100

class ChamberBedFlowHeater:
	def __init__(self, config):
		# setup self
		self.name = 'chamber'
		self.lock = threading.Lock()
		self.printer = config.get_printer()
		self.reactor = self.printer.get_reactor()
		self.target_temp = 0.
		self.last_temp = 0.
		self.fanspeed = 0.
		
		# read configuration
		self.min_temp = config.getfloat('min_temp', minval=KELVIN_TO_CELSIUS)
		self.gcode_id = config.get('gcode_id', 'C')
		self.max_temp = config.getfloat('max_temp', above=self.min_temp)
		self.max_delta = config.getfloat('max_delta', 2.0, above=0.)
		self.min_speed = config.getfloat('min_speed', 0.3, minval=0., maxval=1.)
		self.max_speed = config.getfloat('max_speed', 1., above=0., maxval=1.)
		self.control_duration = config.getfloat('control_duration', 5.)
		self.control_delta = config.getfloat('control_delta', 2., above=0.)
		self.control_step = config.getfloat('control_step', .1, above=0.)
		self.heater_name = config.get('heater_name', 'heater_bed')
		self.heater_max_delta = config.getfloat('heater_max_delta', 2., above=0.)

		# setup fan
		self.fan = fan.Fan(config, default_shutdown_speed=1.)
		 
		# setup Sensor
		pheaters = self.printer.load_object(config, 'heaters')
		self.sensor = pheaters.setup_sensor(config)
		self.sensor.setup_minmax(self.min_temp, self.max_temp)
		self.sensor.setup_callback(self.temperature_callback)

		# find associated heater
		self.heater = pheaters.lookup_heater(self.heater_name);
		
		# register as heater as chamber sensor
		pheaters.register_sensor(config, self, self.gcode_id)
		
		# setup gcode
		gcode = self.printer.lookup_object("gcode")
		gcode.register_mux_command("SET_HEATER_TEMPERATURE", "HEATER", self.name, self.cmd_SET_HEATER_TEMPERATURE, desc=self.cmd_SET_HEATER_TEMPERATURE_help)
		gcode.register_command("M141", self.cmd_M141, desc=self.cmd_M141_help)
		gcode.register_command("M191", self.cmd_M191, desc=self.cmd_M191_help)
		
		# start the timer when ready
		self.printer.register_event_handler("klippy:ready", self._handle_ready)
		

	def temperature_callback(self, read_time, temp):
		with self.lock:
			self.last_temp = temp

	def set_temp(self, degrees):
		if degrees and (degrees < self.min_temp or degrees > self.max_temp):
			raise self.printer.command_error("Requested temperature (%.1f) out of range (%.1f:%.1f)" % (degrees, self.min_temp, self.max_temp))
		with self.lock:
			self.target_temp = degrees
		self.reactor.update_timer(self.timer_handler, self.reactor.monotonic() + self.control_duration)

	def get_temp(self, eventtime):
		with self.lock:
			target_temp = self.target_temp
			last_temp = self.last_temp
		return last_temp, target_temp

	def check_busy(self, eventtime):
		with self.lock:
			target_temp = self.target_temp
			last_temp = self.last_temp
			max_delta = self.max_delta
		return last_temp < target_temp - max_delta

	def stats(self, eventtime):
		with self.lock:
			target_temp = self.target_temp
			last_temp = self.last_temp
			min_temp = self.min_temp
		is_active = target_temp > min_temp
		return is_active, '%s: target=%.0f temp=%.1f ' % (self.name, target_temp, last_temp )

	def get_status(self, eventtime):
		with self.lock:
			target_temp = self.target_temp
			last_temp = self.last_temp
		power = self.fan.get_status(eventtime)["speed"]
		return {'temperature': last_temp, 'target': target_temp, 'power': power}

	cmd_SET_HEATER_TEMPERATURE_help = "Sets a heater temperature"
	def cmd_SET_HEATER_TEMPERATURE(self, gcmd):
		temp = gcmd.get_float('TARGET', 0.)
		pheaters = self.printer.lookup_object('heaters')
		pheaters.set_temperature(self, temp)
		
	cmd_M141_help = "Sets chamber <S> temperature"
	def cmd_M141(self, gcmd, wait=False):
		temp = gcmd.get_float('S', 0.)
		pheaters = self.printer.lookup_object('heaters')
		pheaters.set_temperature(self, temp, wait)

	cmd_M191_help = "Sets chamber <S> temperature and waits"
	def cmd_M191(self, gcmd):
		self.cmd_M141(gcmd, wait=True)
		
	def _handle_ready(self):
		waketime = self.reactor.NEVER
		if self.target_temp:
			waketime = self.reactor.monotonic() + self.control_duration
		self.timer_handler = self.reactor.register_timer(self._timer_event, waketime)

	def _set_fan_speed( self, speed):
		with self.lock:
			fanspeed = self.fanspeed
			self.fanspeed = speed
		if fanspeed != speed:
			curtime = self.printer.get_reactor().monotonic()
			pt = self.fan.get_mcu().estimated_print_time(curtime)			
			self.fan.set_speed( pt + PIN_MIN_TIME, speed)
		
	def _timer_event(self, eventtime):
		with self.lock:
			target_temp = self.target_temp
			last_temp = self.last_temp
			fanspeed = self.fanspeed

		if target_temp == 0.:
			# no target temp
			self._set_fan_speed(0)
			return self.reactor.NEVER
			
		heater_temp, heater_target = self.heater.get_temp(eventtime)
		if heater_target == 0. or heater_temp < (heater_target - self.heater_max_delta):
			self._set_fan_speed(0)
		elif last_temp < target_temp - self.control_delta:		
			self._set_fan_speed(self.max_speed)
		elif last_temp > target_temp + self.control_delta:		
			self._set_fan_speed(0)
		elif fanspeed != 0. and fanspeed < self.max_speed - self.control_step and last_temp < target_temp:		
			self._set_fan_speed(fanspeed + self.control_step)
		elif fanspeed > self.min_speed + self.control_step and last_temp > target_temp:		
			self._set_fan_speed( fanspeed - self.control_step)
			
		return eventtime + self.control_duration
	
def load_config(config):
	return ChamberBedFlowHeater(config)
	
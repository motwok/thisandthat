# Support for waiting on ready state / event
#
# Copyright (C) 2021  Emmo Emminghaus <mo2000@mo2000.de>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

class WaitForRestart:
	def __init__(self, config):
		self.is_printer_ready = False
		self.printer = config.get_printer()
		self.printer.register_event_handler("klippy:ready", self._handle_ready)
		self.printer.register_event_handler("klippy:shutdown", self._handle_shutdown)
		self.gcode = self.printer.lookup_object("gcode")
		self.reactor = self.printer.get_reactor()
		self.gcode.register_command("WAITFORREADY", self.cmd_WAITFORREADY, True, self.cmd_WAITFORREADY_help)

	def _handle_ready(self):
		self.is_printer_ready = True

	def _handle_shutdown(self):
		self.is_printer_ready = False

	cmd_WAITFORREADY_help = "Wait for printer ready"

	def cmd_WAITFORREADY(self, gcmd):
		while not self.is_printer_ready:
			self.reactor.pause(self.reactor.monotonic() + 1.)


def load_config(config):
	return WaitForRestart(config)

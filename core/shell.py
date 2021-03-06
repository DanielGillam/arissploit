#!/usr/bin/env python3

import sys

# Import core modules
from core.module_manager import ModuleManager
from core import colors
from core import command_handler

shellface = "["+colors.bold+"arissploit"+colors.end+"]:"
mm = ModuleManager

def run():
	global shellface
	global mm

	ch = command_handler.Commandhandler(mm, False)

	while True:
		try:
			setFace()
			command = input(shellface+" ")

			ch.handle(command)
		except KeyboardInterrupt:
			sys.exit()

def setFace():
	global shellface
	global mm
	if mm.moduleLoaded == 0:
		shellface = "["+colors.bold+"arissploit"+colors.end+"]:"
	else:
		shellface = "["+colors.bold+"arissploit"+colors.end+"]"+"("+colors.red+mm.moduleName+colors.end+"):"

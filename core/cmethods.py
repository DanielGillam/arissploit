#!/usr/bin/env python3

import sys
import os
import imp
import traceback
import curses
import time
import importlib
import glob

# Import getpath for lib path
from core import getpath

# Append lib path
sys.path.append(getpath.lib())

# Import core modules

from core import helptable
from core import helpin
from core import colors
from core import moduleop
from prettytable import PrettyTable
from core import mscop
from core import value_holder
from core import moddbparser
from core.messages import *
from core.apistatus import *

# Import exceptions
from core.exceptions import UnknownCommand
from core.exceptions import ModuleNotFound
from core.exceptions import VariableError

class Cmethods:

	# Module manager object

	mm = None
	modadd = None

	# Init

	def __init__(self, mmi):
		self.mm = mmi

	# Module custom commands

	def mcu(self, command):
		try:
			if command[0] in self.modadd.customcommands.keys():
				call = getattr(self.modadd, command[0])
				try:
					return call(command[1:])
				except Exception as e:
					print("\033[1;31m[-]\033[0m Unexpected error in module:\n")
					traceback.print_exc(file=sys.stdout)
					print(colors.end)
					if api.enabled == True:
						raise
			else:
				raise UnknownCommand("\033[1;31m[-]\033[0m Unrecognized command!")
		except AttributeError:
			raise UnknownCommand("\033[1;31m[-]\033[0m Unrecognized command!")

	# Built-in commands
	
	def exit(self, args):
		sys.exit()

	def clear(self, args):
		if len(args) != 0 and args[0] == "tmp":
			mscop.clear_tmp()
		else:
			sys.stderr.write("\x1b[2J\x1b[H")

	def os(self, args):
		CYAN = '\033[1;34m'
		ENDL = '\033[0m'
		os.system(' '.join(args))

	def help(self, args):
		print("")
		if self.mm.moduleLoaded == 0:
			print(helptable.generateTable(helpin.commands))
		else:
			try: 
				print(helptable.generatemTable(helpin.mcommands, self.modadd.customcommands))
			except AttributeError:
				print(helptable.generateTable(helpin.mcommands))
			try:
				print('\n',self.modadd.help_notes,'\n')
			except AttributeError:
				pass
		print("")

	def netifs(self, args):
		os.system("ifconfig")

	def scan(self, args):
		network_scanner = importlib.import_module("core.network_scanner")
		network_scanner.scan()
		del network_scanner

	def use(self, args):
		if 1:
			try:
				init = False
				if "modules."+args[0] not in sys.modules:
					init = True
			except:
				printError("Please enter module name!")
				return

			if self.mm.moduleLoaded == 0:
				try:
					self.modadd = importlib.import_module("modules."+args[0])
					self.mm.moduleLoaded = 1
					self.mm.setName(self.modadd.conf["name"])
					try:
						print(self.modadd.conf["message"])
					except KeyError:
						pass
					try:
						if self.modadd.conf["outdated"] == 1:
							printWarning("This module is outdated and might not be working.")
					except KeyError:
						pass
					try:
						if self.modadd.conf["needroot"] == 1:
							if not os.geteuid() == 0:
								printWarning("This module requires root permissions.")
					except KeyError:
						pass
					if init == True:
						try:
							self.modadd.init()
						except AttributeError:
							pass
				except ImportError:
					print("\033[1;31m[-]\033[0m Module is not found!")
					raise ModuleNotFound("\033[1;31m[-]\033[0m Module is not found!")
				except IndexError:
					print("\033[1;31m[-]\033[0m Module is not found!")
					raise ModuleNotFound("\033[1;31m[-]\033[0m Module is not found!")
				except:
					print("\033[1;31m[-]\033[0m Unexpected error in module:\n")
					traceback.print_exc(file=sys.stdout)
					print(colors.end)
					if api.enabled == True:
						raise
			else:
				print("\033[1;31m[-]\033[0m Module already in use!")

	def modules(self, args):
		t = PrettyTable([colors.bold+'Modules:', ''+colors.end])
		t.align = 'l'
		t.valing = 'm'
		t.border = False
		xml = moddbparser.parsemoddb()
		root = xml[0]
		for category in root:
			if category.tag == "category":
				t.add_row(["", ""])
				t.add_row([colors.red+colors.uline+category.attrib["name"]+colors.end, colors.red+colors.uline+"Description"+colors.end])

			for item in category:
				if item.tag == "module":
					for child in item:
						if child.tag == "shortdesc":
							t.add_row([item.attrib["name"], child.text])
							break
		print("")
		print(t)
		print("")

	def options(self, args):
		try:
			moduleop.printoptions(self.modadd)
		except:
			print("\033[1;31m[-]\033[0m Unexpected error in module:\n")
			traceback.print_exc(file=sys.stdout)
			print(colors.end)
			if api.enabled == True:
				raise

	def back(self, args):
		if self.mm.moduleLoaded == 1:
			self.mm.moduleLoaded = 0
			self.mm.moduleName = ""
		else:
			raise UnknownCommand("\033[1;31m[-]\033[0m Unrecognized command!")

	def reload(self, args):
		try:
			if self.mm.moduleLoaded == 0:
				try:
					mod = "modules."+args[0]
					if mod in sys.modules:
						value_holder.save_values(sys.modules[mod].variables)
						importlib.reload(sys.modules[mod])
						value_holder.set_values(sys.modules[mod].variables)
						try:
							self.modadd.init()
						except AttributeError:
							pass
						print("["+colors.bold+colors.green+"suc"+colors.end+"] Module "+ args[0] +" reloaded!"+colors.end)
					else:
						importlib.import_module(mod)
						try:
							self.modadd.init()
						except AttributeError:
							pass
						print("["+colors.bold+colors.green+"suc"+colors.end+"] Module "+ args[0] +" imported!"+colors.end)

				except IndexError:
					print (colors.red+"Please enter module's name"+colors.end)
			else:
				try:
					mod = "modules."+args[0]
					if mod in sys.modules:
						value_holder.save_values(sys.modules[mod].variables)
						importlib.reload(sys.modules[mod])
						value_holder.set_values(sys.modules[mod].variables)
						try:
							self.modadd.init()
						except AttributeError:
							pass				
						print("["+colors.bold+colors.green+"suc"+colors.end+"] Module "+ args[0] +" reloaded!"+colors.end)
					else:
						importlib.import_module(mod)
						try:
							self.modadd.init()
						except AttributeError:
							pass
						print("["+colors.bold+colors.green+"suc"+colors.end+"] Module "+ self.mm.moduleName +" reloaded!"+colors.end)
				except IndexError:
					mod = "modules."+self.mm.moduleName
					if mod in sys.modules:
						value_holder.save_values(sys.modules[mod].variables)
						importlib.reload(sys.modules[mod])
						value_holder.set_values(sys.modules[mod].variables)
						try:
							self.modadd.init()
						except AttributeError:
							pass
						print("["+colors.bold+colors.green+"suc"+colors.end+"] Module "+ self.mm.moduleName +" reloaded!"+colors.end)

					else:
						modadd = importlib.import_module(mod)
						try:
							self.modadd.init()
						except AttributeError:
							pass
						print("["+colors.bold+colors.green+"suc"+colors.end+"] Module "+ self.mm.moduleName +" reloaded!"+colors.end)
		except:
			print("\033[1;31m[-]\033[0m Faced unexpected error during reimporting:\n")
			traceback.print_exc()
			print(colors.end)
			if api.enabled == True:
				raise

	def run(self, args):
		if self.mm.moduleLoaded == 1:
			try:
				return self.modadd.run()

			except KeyboardInterrupt:
				print("\033[1;31m[-]\033[0m Module terminated!"+colors.end)
			except PermissionError:
				printError("Permission denied!")
				return "[-] Permission denied!"
			except:
				print("\033[1;31m[-]\033[0m Unexpected error in module:\n")
				traceback.print_exc(file=sys.stdout)
				print(colors.end)
				if api.enabled == True:
					raise
		else:
			raise UnknownCommand("\033[1;31m[-]\033[0m Module is not loaded!")

	def set(self, args):
		try:
			self.modadd.variables[args[0]][0] = args[1]
			print(colors.bold+args[0] +" ==> "+ str(args[1]) + colors.end)

		except (NameError, KeyError):
			print("\033[1;31m[-]\033[0m Option is not found!")
			raise VariableError("\033[1;31m[-]\033[0m Option is not found!")
		except IndexError:
			print("\033[1;31m[-]\033[0m Invalid value!")
			raise VariableError("\033[1;31m[-]\033[0m Invalid value!")
		except:
			print("\033[1;31m[-]\033[0m Unexpected error in module:\n")
			traceback.print_exc(file=sys.stdout)
			print(colors.end)
			if api.enabled == True:
				raise

	def create(self, args):
		try:
			try:
				completeName = os.path.join(getpath.modules(), args[0]+".py")
				if os.path.exists(completeName):
					print("\033[1;31m[-]\033[0m Module already exists!"+colors.end)

				else:
					mfile = open(completeName, 'w')
					template = os.path.join('core', 'module_template')
					f = open(template, 'r')
					template_contents = f.readlines()
					template_contents[5] = "	\"name\": \""+args[0]+"\", # Module's name (should be same as file name)\n"
					template_contents[11] = "	\"initdate\": \""+(time.strftime("%d.%m.%Y"))+"\", # Initial date\n"
					template_contents[12] = "	\"lastmod\": \""+(time.strftime("%d.%m.%Y"))+"\", # Last modification\n"
					mfile.writelines(template_contents)
					mfile.close()
					printSuccess("Saved to modules/"+ args[0] +".py!")

			except IndexError:
				printError("Please enter module name!")

			except PermissionError:
				printError("Permission denied!")

			except IOError:
				printError("Something went wrong!")

		except IndexError:
			raise UnknownCommand("\033[1;31m[-]\033[0m Unrecognized command!")

	def update(self, args):
		os.system("chmod +x etc/update.sh && etc/update.sh")

	def deps(self, args):
		if self.mm.moduleLoaded == 0:
			modules = glob.glob(getpath.modules()+"*.py")
			dependencies = []
			for module in modules:
				try:
					modadd = importlib.import_module("modules."+os.path.basename(module).replace(".py", ""))
					for dep in modadd.conf["dependencies"]:
						if dep not in dependencies:
							dependencies.append(dep)
				except ImportError:
					print("\033[1;31m[-]\033[0m ImportError: "+os.path.basename(module).replace(".py", "")+colors.end)
					break
				except KeyError:
					pass
			for dep in dependencies:
				print(dep)
		else:
			try:
				for dep in self.modadd.conf["dependencies"]:
					print(dep)
			except KeyError:
				printWarning("This module does not require any dependencies.")
					
	def init(self, args):
		if self.mm.moduleLoaded == 1:
			try:
				self.modadd.init()
				printSuccess("Module has been initialized!")
			except AttributeError:
				printError("This module does not have init function!")
		else:
			raise UnknownCommand("\033[1;31m[-]\033[0m Unrecognized command!")

	def redb(self, args):
		if self.mm.moduleLoaded == 1:
			try:
				moduleop.addtodb(self.modadd)
			except PermissionError:
				print("\033[1;31m[-]\033[0m Permission denied!"+colors.end)
			except KeyboardInterrupt:
				print()
			except:
				print("\033[1;31m[-]\033[0m Faced unexpected:\n")
				traceback.print_exc(file=sys.stdout)
				print(colors.end)
				if api.enabled == True:
					raise

		else:
			if True:
				try:
					modules = glob.glob(getpath.modules()+"*.py")
					for module in modules:
						module = module.replace(getpath.modules(), '').replace('.py', '')
						if module != '__init__' and module != "test":
							modadd = importlib.import_module("modules."+module)
							moduleop.addtodb(modadd)
				except PermissionError:
					print("\033[1;31m[-]\033[0m Permission denied!"+colors.end)
				except KeyboardInterrupt:
					print()
				except:
					print("\033[1;31m[-]\033[0m Faced unexpected:\n")
					traceback.print_exc(file=sys.stdout)
					print(colors.end)
					if api.enabled == True:
						raise

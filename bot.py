#!/usr/bin/env python
# Copyright (c) 2005-2012 kang@insecure.ws, dirty code licensed under the GPLv2
# See LICENSE for details

import sys, urllib, select, re
import time, threading, thread
import random
import signal, os
import traceback
from socket import *
import ssl
import modules
import config

joined = 0

def debug(msg):
	if config.debug == 1:
		print "== Debug ==\n"
		print msg
		print "==       ==\n"

def die(msg):
	print msg
	sys.exit()

def handleKeyboardInterrupt( signalNumber, frame ) :
	print "> Sending kill signal to all modules."
	try:
		for i in modules.mod_list:
			sys.modules[i].die()
			print ">\tKilled ", i
	except:
		traceback.print_exc()
	print "> Exiting."
	sys.exit()

def reload_modules():
	print "> (Re)loading modules."
	globals()["bot_chan_handlers"]={}
	globals()["bot_msg_handlers"]={}
	globals()["bot_scheduler_handlers"]={}
	try:
		for i in modules.mod_list:
			sys.modules[i].die()
			del(sys.modules[i])
			print ">\tRemoved: ", i
	except:
		traceback.print_exc()
	reload(modules)
	try:
		for i in modules.mod_list:
			globals()['bot_chan_handlers'][i] = sys.modules[i].chan_handlers
			globals()['bot_msg_handlers'][i]  = sys.modules[i].msg_handlers
			globals()['bot_scheduler_handlers'][i] = sys.modules[i].scheduler_handlers
			sys.modules[i].init()
			print ">\tLoaded: ", i
	except:
		traceback.print_exc()

def bot_connect(tsocket):
	# Connect to IRC
	print "> Connected to "+config.server+"."
	tsocket.send('NICK %s\r\n' % config.nick)
	tsocket.send('USER %s 0 * : %s\r\n' % (config.nick, config.nick))
	if len(config.passwd) > 1:
		tsocket.send('PRIVMSG nickserv : identify %s\r\n' % config.passwd)

def bot_join(tsocket):
	# Join channel
	if config.channel_password != None:
		tsocket.send('JOIN %s %s\r\n' % (config.channel, config.channel_password))
	else:
		tsocket.send('JOIN %s\r\n' % config.channel)
	print "> Joined "+config.channel+"."

def check_flood(flood_time):
	if (time.time() - flood_time) <  config.max_flood:
		print "!Getting flooded of requests, ignoring (max_flood is " + str(config.max_flood) + " > " + str((time.time() - flood_time)) + ")"
		return 1
	return 0

class Scheduler(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		while 1:
			time.sleep(5)
			for i in bot_scheduler_handlers:
				try:
					actions = sys.modules[i].scheduler_handler(config.channel)
					if len(actions) != 0:
						for y in actions: tsocket.send(y)
				except AttributeError:
					pass
				except:
					traceback.print_exc()

signal.signal(signal.SIGINT, handleKeyboardInterrupt)
flood_time = time.time()
t = Scheduler()

print "> 	  Stupid bot, licensed under the terms of the GPL          <"
reload_modules()

s = socket(AF_INET, SOCK_STREAM)
s.connect((config.server, config.port))
if config.ssl:
	tsocket = ssl.SSLSocket(s)
else:
	tsocket = s

isr0 = [tsocket]
isw0 = []
ise0 = []
bot_connect(tsocket)
t.start()

# Starting client loop for messages
while 1:
	r0, w0, e0 = select.select(isr0, isw0, ise0, 0.5)
	if e0:
		print "> Connection error has occured. Reconnecting."
		bot_connect(tsocket)
		joined =0
	if r0:
		data = tsocket.recv(1024)
		debug(data);
		if not joined:
			if data.find("End of /MOTD command") > 0:
				bot_join(tsocket)
				joined = 1
		# Global IRC messages
		if data.startswith("PING"):
			tsocket.send('PONG %s\r\n' % data.split(":")[1])
		
		# Check for IRC commands
		try:
			cmd = data.split(" ")[1];
		except IndexError:
			continue

		if cmd == "433":
			#Nick already in use
			tsocket.send('NICK ArcSight%s\r\n' % str(random.random())[2:8])
			time.sleep(3)
			tsocket.send('PRIVMSG nickserv : recover ArcSight %s\r\n' % config.passwd)
			time.sleep(3)
			tsocket.send('PRIVMSG nickserv : release ArcSight %s\r\n' % config.passwd)
			time.sleep(3)
			tsocket.send('NICK %s\r\n' % config.nick)

		elif cmd == "451":
			#Not registered
			tsocket.send('PRIVMSG nickserv : identify %s\r\n' % config.passwd)
			time.sleep(1)

		elif cmd == "PRIVMSG":
			if check_flood(flood_time):
				continue

			# Private messages
			msg = data.split(" ")[3]
			try:
				if msg.startswith(":VERSION"):
					tsocket.send('PRIVMSG %s :%s\r\n' % (data.split("!")[0][1:], config.version))
					flood_time = time.time()
					continue
				elif msg.startswith(":refresh"):
					tsocket.send('PRIVMSG %s :denied.\r\n' % (data.split("!")[0][1:]))
					flood_time = time.time()
#					reload_modules()
					continue
			except:
				print "!Private message parsing error (internal)."
				traceback.print_exc()

			try:
				for i in bot_msg_handlers:
					for x in bot_msg_handlers[i]:
						if msg.startswith(x):
							debug("got matching msg command"+x+" for module"+i)
							flood_time = time.time()
							# freenode only.
							nick = data.split(":")[1].split("!")[0]
							args = data.split(":")[2].split("\r\n")[0].split(" ")[1:]
							action = sys.modules[i].privmsg_handler(nick,
												x,
												args)
							tsocket.send(action)
							continue
			except:
				print "!Private message parssing error (module)."
				traceback.print_exc()

			# Channel messages
			msg = data.split(":")[2]
			try:
				for i in bot_chan_handlers:
					for x in bot_chan_handlers[i]:
						if msg.startswith(x):
							debug("got matching chan command "+x+"for module "+i)
							flood_time = time.time()
							# freenode only.
							nick = data.split(":")[1].split("!")[0]
							args = data.split(":")[2].split("\r\n")[0].split(" ")[1:]
							action = sys.modules[i].chanmsg_handler(config.channel,
												nick,
												x,
												args)
							tsocket.send(action)
							continue
			except:
				print "!Channel message parsing error (module)."
				traceback.print_exc()

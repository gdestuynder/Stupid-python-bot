import os, sys

__info__ = {'author': 'kang',
		'email': 'kang@insecure.ws',
		'version': '1',
		'date': '07-11-2005' }

chan_handlers = ['#', "!bug"]
msg_handlers = ['himantis']

def init():
	print "[mantis initializing]"

def chanmsg_handler(nick, cmd, args):
	print "[mantis got "+nick+" cmd ", cmd, " args ",args, "]"

def privmsg_handler(nick, msg):
	print "[mantis got ",nick," ",msg

def die():
	print "[mantis dying]"

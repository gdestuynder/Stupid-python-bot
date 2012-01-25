import asyncore, asynchat
import traceback
import time
import re
import os, socket, string, sys
import threading

#should use Queue
#queue should kill asyncore for refresh

__info__ = {'author': 'kang',
		'email': 'gdestuynder@mozilla.com',
		'version': '1',
		'date': '19-09-2011' }

chan_handlers = []
msg_handlers = []
scheduler_handlers = ["get_msg"]
actions = []
PORT = 6668
s = asyncore.dispatcher

colors = {'red': '\x034\x02',
	'normal': '\x03\x02',
	'blue': '\x032\x02',
	'green': '\x033\x02',
	'yellow': '\x038\x02',
}
severity = {'INFORMATIONAL': colors['yellow'],
	'CRITICAL': colors['red'],
}

class Channel(asynchat.async_chat):
	def __init__(self, server, sock, addr):
		asynchat.async_chat.__init__(self, sock)
		self.set_terminator("\r\n")
		self.data = ""
		self.shutdown = 0

	def collect_incoming_data(self, data):
		self.data = self.data + data

	def san(self, data):
		return data.strip('\r').strip('\n')

	def found_terminator(self):
		self.push("200 OK\r\n")
		self.close_when_done()
		globals()["actions"].append(self.san(self.data))

class Server(asyncore.dispatcher):
	def __init__(self, port):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		while True:
			try:
				self.bind(("", port))
				break
			except:
				print traceback.print_exc()
				time.sleep(3)
		self.listen(5)

	def handle_accept(self):
		conn, addr = self.accept()
#		print "AS >> New connection from", addr
		Channel(self, conn, addr)

class Network(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.s = Server(PORT)

	def run(self):
		asyncore.loop()

def init():
	t = Network()
	t.start()
	print "[AS listening for events on", PORT, "]"

def chanmsg_handler(nick, cmd, args):
	return

def privmsg_handler(nick, msg):
	return

def colorify(data):
	for i in severity:
		data = data.replace(i, severity[i]+i+colors['normal'], 1)
	return data

def parse(data):
	socket.setdefaulttimeout(3)
	ip = None
	try:
		ip = re.findall("(?:\d{1,3}\.){3}\d{1,3}", data)[0]
		host = ip
		host = socket.gethostbyaddr(ip)[0]
	except:
		pass
	if ip != None:
		data = data.replace(ip, host+' ('+ip+')', 1)
	data = data.replace('->', ' -> ', 1)
	return colorify(data)

def scheduler_handler(channel):
	tmp = []
	for i in globals()["actions"]:
		tmp.append('PRIVMSG %s : %s\r\n' % (channel, parse(i)))
	globals()["actions"] = []
	return tmp

def die():
	return

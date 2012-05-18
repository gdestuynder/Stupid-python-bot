import os, sys
import SOAP
import google
__info__ = {	'author': 'kang',
		'email': 'kang@insecure.ws',
		'version': '1',
		'date': '08-11-2005' }

chan_handlers = ['!gg']
msg_handlers = []

def init():
	google.setLicense("whatever")

def chanpriv_handler(nick, cmd, args):
	raise UnhandledFunction
	
def chanmsg_handler(channel, nick, cmd, args):
	g = sys.modules['gg']
	action = ""
	q = " "
	for i in args: q += i+" "
	spell = google.doSpellingSuggestion(q)
	if spell != None:
		action = 'PRIVMSG %s :Perhaps you mean %s?\r\n' % (channel, spell)
		data = google.doGoogleSearch(spell)
		action += 'PRIVMSG %s :Then it would be %s .. else:\r\n' % (channel, data.results[0].URL)	
	data = google.doGoogleSearch(q)
	action += 'PRIVMSG %s :%s\r\n' % (channel, data.results[0].URL)
	return action

def die():
	raise UnhandledFunction

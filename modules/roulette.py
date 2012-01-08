import os, sys
import random
__info__ = {	'author': 'kang',
		'email': 'kang@insecure.ws',
		'version': '1',
		'date': '07-11-2005' }

chan_handlers = ['!r']
msg_handlers = []
scheduler_handlers = []

gun_max_load = 6
gun_bullet_slot = random.randint(1, gun_max_load)
gun_current_slot = 0


def init():
	gun_max_load = 6
	gun_bullet_slot = random.randint(1, gun_max_load)
	gun_current_slot = 0
	
def chanmsg_handler(channel, nick, cmd, args):
	r = sys.modules['roulette']
	r.gun_current_slot = r.gun_current_slot + 1
	if r.gun_current_slot == r.gun_max_load:
		action = 'PRIVMSG %s :im not gonna kill you this time... another try ?\r\n' % (channel)
		r.gun_bullet_slot = random.randint(1, r.gun_max_load)
		r.gun_current_slot = 0
		return action
	if r.gun_current_slot == r.gun_bullet_slot:
		action = 'PRIVMSG %s :*BANG*. %s is lying on the floor.\r\n' % (channel, nick)
		r.gun_bullet_slot = random.randint(1, r.gun_max_load)
		r.gun_current_slot = 0
	else:
		action = 'PRIVMSG %s :*click* (slot %s)\r\n' % (channel, r.gun_current_slot)
	return action

def die():
	return

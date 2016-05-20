# coding: utf-8
import parser
import socket
import Queue
import thread
import traceback
import time
import json
import atexit
import urllib2
from time import sleep
from threading import Timer
HOST = "irc.twitch.tv"
PORT = 6667
WHOST = "chatdepot.twitch.tv"
WPORT = 6667
NICK = "squid_coin_bot"
PASS = "oauth:oju0t5n0yo3cia31ohaz8w9uqv35b2"
CHAN = "drowsysquid75"
class Bot(object):
	def __init__(self, nick, pasw, chan):
		#socket for sending
		self.s = socket.socket()
		#socket for recieving
		self.r = socket.socket()
		#socket for whispering
		self.w = socket.socket()
		#global work queue (comands are queued here)
		self.q = Queue.Queue()
		self.nick = nick
		self.pasw = pasw
		self.chan = chan
		self.commands = {}
		self.chatlog = []
		#{username: {currency:0, is_online:True or False}} done this way so that users can add custom attributs to the user dictonary
		self.users = {}
		self.timers = {}
		self.threads_alive = True
	def chat(self, msg):
		#send a chat message using the sending socket
		self.s.send("PRIVMSG #%s : %s\r\n" %(self.chan, msg))
	def whisper(self, target, msg):
		self.w.send("PRIVMSG #jtv :/w %s %s\r\n" % (target, msg))
	def connect(self, host, port):
		#connect the sending socket
		self.s.connect((host, port))
		self.s.send("PASS %s\r\n" %self.pasw)
		self.s.send("NICK %s\r\n" %self.nick)
		self.s.send("JOIN #%s\r\n" %self.chan)
		#and the recieving socket
		self.r.connect((host, port))
		self.r.send("PASS %s\r\n" %self.pasw)
		self.r.send("NICK %s\r\n" %self.nick)
		self.r.send("JOIN #%s\r\n" %self.chan)
		#and finally the whispering socket
		self.w.connect((host, port))
		self.w.send("PASS %s\r\n" %self.pasw)
		self.w.send("NICK %s\r\n" %self.nick)
		self.w.send("JOIN #%s\r\n" %self.chan)
		self.w.send("CAP REQ :twitch.tv/commands\r\n")
		print "connected"
	#commands must run without fail so they tried until they can be appended to the queue
	def command(self, command, mess):
		def command_thread(self, command, mess):
			while self.threads_alive:
				try:
					self.q.put((command, mess))
					break
				except:
					pass
		thread.start_new_thread(command_thread(self, command, mess))
	#start processing queued commands 
	def start_working(self):
		def worker(self):
			while self.threads_alive:
				try:
					command, mess = self.q.get()
					command(mess, self)
				except:
					pass
		thread.start_new_thread(worker, (self,))
	#add a commmand to the list of items to be checked
	def add_command(self, command):
		self.commands.update({command.keyword:command.action})
	def add_timer(self, timer, args):
		self.timers.update({timer.name: [timer(), args]})
	def start_recieving(self):
		def reciever(self):
			while self.threads_alive:
				try:
					mess = self.r.recv(2048)
					print mess
					username = mess.split("@")[0].split("!")[1]
					mess = mess.split("PRIVMSG #%s :" % (self.chan))[1].split("\r\n")[0]
					if username != self.nick and "GLHF" not in mess and "GLHF" not in username:
						self.chatlog.append([username, mess])
				except:
					if "PING" in mess:
						self.s.send("PONG :tmi.twitch.tv\r\n")
		thread.start_new_thread(reciever, (self,))
	def start_detection(self):
		def detection_thread(self):
			checked = []
			while self.threads_alive:
				try:
					for key in self.commands.keys():
						#makes sure only one command per chat
							if key in self.chatlog[0][1]:
								self.command(self.commands[key], self.chatlog[0])
								self.chatlog.remove(self.chatlog[0])
							#keeps track of all commands checked
							if key not in self.chatlog[0][1]:
								checked.append(key)
							#if no chat commands were found in chatlog, remove it
							if sorted(checked) == sorted(self.commands.keys()):
								self.chatlog.remove(self.chatlog[0])
				except:
					pass
		thread.start_new_thread(detection_thread, (self,))
	def start_timers(self):
		def bot_timer(t, botself,args):
			t.bot = botself
			t.timer(*args)
		for timer in self.timers:
			thread.start_new_thread(bot_timer, (self.timers[timer][0],self,self.timers[timer][1]))
	def start_bot(self):
		self.start_working()
		self.start_recieving()
		self.start_detection()
		self.start_timers()
"""
How to implement a command
class command(object):
	def __init__(self):
		self.keyword = ?
	def action(self, mess, botself):
		pass
"""
"""
How to implement a timer
class timer(object):
	def __init__(self):
		self.bot = None
	def timer(self):
		if self.bot.threads_alive:
			print self.bot.threads_alive
			print "This is an example timer"
			timer = Timer(5, self.timer)
			thread.start_new_thread(timer.run, ())
"""
class command(object):
	def __init__(self):
		self.keyword = "!test"
	def action(self, mess, botself):
		pass
class command(object):
	def __init__(self):
		self.keyword = "!give "
	def action(self, mess, botself):
		pass
class get_new_users(object):
	def __init__(self):
		self.bot = None
	name = "get_new_users"
	def timer(self):
		users_online = json.loads(urllib2.urlopen("https://tmi.twitch.tv/group/user/%s/chatters" % CHAN).read())["chatters"]
		for user in users_online["viewers"] + users_online["staff"] + users_online["admins"] + users_online["global_mods"]:
			if user in self.bot.users.keys():
				if self.bot.users[user]["is_online"]:
					pass
				elif not self.bot.users[user]["is_online"]:
					self.bot.users[user]["is_online"] = True
			elif user not in self.bot.users.keys():
				self.bot.users.update({user: {"currency" : 0, "is_online": True, "is_mod": False}})
		for user in users_online["moderators"]:
			if user in self.bot.users.keys():
				if self.bot.users[user]["is_online"]:
					pass
				elif not self.bot.users[user]["is_online"]:
					self.bot.users[user]["is_online"] = True
			elif user not in self.bot.users.keys():
				self.bot.users.update({user: {"currency" : 0, "is_online": True, "is_mod": True}})
		if self.bot.threads_alive:
			x = Timer(1, self.timer)
			thread.start_new_thread(x.run, ())
class handout_currency(object):
	def __init(self):
		self.bot = None
	name = "handout_currency"
	def timer(self, time, amount):
		for user in self.bot.users:
			if self.bot.users[user]["is_online"]:
				self.bot.users[user]["currency"] += amount
		if self.bot.threads_alive:
			x = Timer(time, self.timer, args=[time, amount])
			thread.start_new_thread(x.run, ())
mr = Bot(NICK, PASS, CHAN)
mr.connect(HOST, PORT)
mr.add_timer(get_new_users, ())
mr.add_timer(handout_currency, (1,10))
mr.start_bot()
mr.whisper("drowsysquid75", "test")
x = ""
while x == "":
	x = raw_input()
mr.threads_alive = False
print mr.users
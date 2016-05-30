# coding: utf-8
import socket
import Queue
import thread
import traceback
import time
import json
import urllib2
import pickle
import os
import random
import atexit
from threading import Timer
HOST = "irc.twitch.tv"
PORT = 6667
WHOST = "irc.chat.twitch.tv"
WPORT = 6667
NICK = "squid_coin_bot"
PASS = "oauth:oju0t5n0yo3cia31ohaz8w9uqv35b2"
CHAN = "drowsysquid75"
currency_name = "SquidBux"
class Bot(object):
	def __init__(self, nick, pasw, chan):
		#socket for sending
		self.s = socket.socket()
		#socket for recieving
		self.r = socket.socket()
		#socket for whispering
		self.w = socket.socket()
		#global work queue (commands are queued here)
		self.wr = socket.socket()
		self.q = Queue.Queue()
		self.nick = nick
		self.pasw = pasw
		self.chan = chan
		self.commands = {}
		self.chatlog = []
		#{username: {currency:0, is_online:True or False, is_mod: True or False}} done this way so that users can add custom attributs to the user dictonary
		self.users = {}
		self.timers = {}
		self.storage = {}
		self.threads_alive = True
		self.whisper_log = []
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
		self.w.send("JOIN #jtv\r\n")
		self.w.send("CAP REQ :twitch.tv/commands\r\n")
		#and the one for recieving
		self.wr.connect((WHOST, WPORT))
		self.wr.send("PASS %s\r\n" %self.pasw)
		self.wr.send("NICK %s\r\n" %self.nick)
		self.wr.send("JOIN #jtv\r\n")
		self.wr.send("CAP REQ :twitch.tv/commands\r\n")
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
		thread.start_new_thread(command_thread, (self, command, mess))
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
					username = mess.split("@")[0].split("!")[1]
					mess = mess.split("PRIVMSG #%s :" % (self.chan))[1].split("\r\n")[0]
					print username +" : "+ mess
					if username != self.nick and "GLHF" not in mess and "GLHF" not in username:
						self.chatlog.append({"username": username, "message": mess})
				except:
					if "PING" in mess:
						self.s.send("PONG :tmi.twitch.tv\r\n")
		thread.start_new_thread(reciever, (self,))
	def start_recieving_whispers(self):
		def reciever(self):
			while self.threads_alive:
				try:
					mess = self.wr.recv(2048)
					print mess
					username = mess.split("@")[0].split("!")[1]
					mess = mess.split("WHISPER %s :" % (self.nick))[1].split("\r\n")[0]
					print "whisper:  "+username +" : "+ mess
					if username != self.nick and "GLHF" not in mess and "GLHF" not in username:
						self.whisper_log.append({"username": username, "message": mess})
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
							if key in self.chatlog[0]["message"]:
								self.command(self.commands[key], self.chatlog[0])
								self.chatlog.remove(self.chatlog[0])
								checked = []
							#keeps track of all commands checked
							if key not in self.chatlog[0]["message"]:
								checked.append(key)
							#if no chat commands were found in chatlog, remove it
							if sorted(checked) == sorted(self.commands.keys()):
								self.chatlog.remove(self.chatlog[0])
								checked = []
				except:
					pass
		thread.start_new_thread(detection_thread, (self,))
	def start_timers(self):
		def bot_timer(t, botself,args):
			t.bot = botself
			t.timer(*args)
		for timer in self.timers:
			thread.start_new_thread(bot_timer, (self.timers[timer][0],self,self.timers[timer][1]))
	def load_mods(self):
		try:
			for file in os.listdir("mods"):
				exec(open(os.path.join("mods", file), 'r').read())
		except:
			traceback.print_exc()
			os.mkdir("mods")
	def load_save(self):
		try:
			x = pickle.load(open("save.p", 'rb'))
			self.storage = x["storage"]
			self.users = x["users"]
		except:
			pass
	def start_bot(self):
		self.load_save()
		self.load_mods()
		self.start_working()
		self.start_recieving()
		self.start_recieving_whispers()
		self.start_detection()
		self.start_timers()
		self.chat("Squid_Coin_Bot has joined the channel!")
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
bot = Bot(NICK, PASS, CHAN)
bot.connect(HOST, PORT)
bot.start_bot()
def this():
	bot.threads_alive = False
	bot.chat("Squid_Coin_Bot parting...")
atexit.register(this)
x = ""
while x == "":
	x = raw_input()
bot.threads_alive = False
print bot.users
print bot.chatlog
print bot.storage
pickle.dump({"storage": bot.storage, "users": bot.users}, open("save.p", 'wb'))
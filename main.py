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
import types
from BotConfig import *
class User(object):
	def __init__(self, name):
		self.name = name
		self.currency = 0
		self.time = 0
		self.is_mod = None
		self.is_online = True
class Storage(object):
	def __init__(self):
		pass
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
		self.users = {}
		self.timers = {}
		self.storage = Storage()
		self.threads_alive = True
		self.whisper_log = []
	def connect(self):
		#connect the sending socket
		self.s.connect((HOST, PORT))
		self.s.send("PASS %s\r\n" %self.pasw)
		self.s.send("NICK %s\r\n" %self.nick)
		self.s.send("JOIN #%s\r\n" %self.chan)
		#and the recieving socket
		self.r.connect((HOST, PORT))
		self.r.send("PASS %s\r\n" %self.pasw)
		self.r.send("NICK %s\r\n" %self.nick)
		self.r.send("JOIN #%s\r\n" %self.chan)
		#and finally the whispering socket
		self.w.connect((HOST, PORT))
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
		print "Sockets connected."
	#make the bot execute something; fails if it cannot execute it after three tries
	def bot_command(self, command, kwargs):
		if isinstance(kwargs, dict) and isinstance(command, types.FunctionType):
			def command_thread(self, command, kwargs):
				while self.threads_alive:
					try:
						self.q.put((command, kwargs))
						break
					except:
						traceback.print_exc()
						pass
			thread.start_new_thread(command_thread, (self, command, kwargs))
		else:
			print "Command must be a function and kwargs must be a dict"
	#start processing queued commands 
	def start_working(self):
		def worker(self):
			while self.threads_alive:
				try:
					command, kwargs = self.q.get()
					kwargs.update({"bot": self})
					command(**kwargs)
				except:
					traceback.print_exc()
		thread.start_new_thread(worker, (self,))
	def start_recieving(self):
		def reciever(self):
			mess = ""
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
			mess = ""
			while self.threads_alive:
				try:
					mess = self.wr.recv(2048)
					username = mess.split("@")[0].split("!")[1]
					mess = mess.split("WHISPER %s :" % (self.nick))[1].split("\r\n")[0]
					print "whisper:  "+username +" : "+ mess
					if username != self.nick and "GLHF" not in mess and "GLHF" not in username:
						self.whisper_log.append({"username": username, "message": mess})
				except:
					if "PING" in mess:
						self.s.send("PONG :tmi.twitch.tv\r\n")
		thread.start_new_thread(reciever, (self,))
	def add_command(self, command):
		if isinstance(command, types.ClassType):
			try:
				self.commands.update({command.keyword: command})
			except:
				print "self.keyword of class must be present when definining a command"
		else:
			print "Command must be a class"
	def load_modules(self):
		try:
			for file in os.listdir("mods"):
				try:
					exec(open(os.path.join("mods", file), 'r').read())
				except:
					print "Failed to exec file named %s" % (file)
		except:
			try:
				os.mkdir("mods")
			except:
				print "Failed to load mods. Is the folder named mods missing?"
	def get_users(self):
		def get_users_thread(self):
			while self.threads_alive:
				try:
					users_online = json.loads(urllib2.urlopen("https://tmi.twitch.tv/group/user/%s/chatters" % CHAN).read())["chatters"]
					for user in users_online["viewers"] + users_online["staff"] + users_online["admins"] + users_online["global_mods"]:
						if user in self.users.keys():
							if self.users[user].is_online:
								pass
							elif not self.users[user].is_online:
								self.users[user].is_online = True
								print "%s came online" % (user)
							if self.users[user].is_mod:
								self.users[user].is_mod = False
						elif user not in self.users.keys():
							self.users.update({user: User(user)})
							print "New user %s" % (user)
					for user in users_online["moderators"]:
						if user in self.users.keys():
							if self.users[user].is_online:
								pass
							elif not self.users[user].is_online:
								self.users[user].is_online = True
								print "%s came online" % (user)
							if not self.users[user].is_mod:
								self.users[user].is_mod = True
						elif user not in self.users.keys():
							self.users.update({user: User(user)})
							print "New user %s" % (user)
					for user in self.users.keys():
						if user not in users_online["viewers"] + users_online["staff"] + users_online["admins"] + users_online["global_mods"] + users_online["moderators"]:
							self.users[user].is_online = False
					time.sleep(1)
				except:
					pass
		thread.start_new_thread(get_users_thread, (self,))
	def auto_save(self):
		while self.threads_alive:
			try:
				pickle.dump({"storage": self.storage, "users":self.users}, open("save.p", "wb"))
				time.sleep(15)
			except:
				pass
	def load_save(self):
		try:
			save = pickle.load(open("save.p", "rb"))
			self.storage = save["storage"]
			self.users = save["users"]
		except:
			pass
	def bot_give(self, target, amount):
		self.users[target].currency += amount
	def start_bot(self):
		self.load_save()
		self.load_modules()
		self.connect()
		self.start_recieving()
		self.start_recieving_whispers()
		self.get_users()
		self.start_working()
		self.auto_save()
bot = Bot(NICK, PASS, CHAN)
bot.start_bot()
while True:
	pass
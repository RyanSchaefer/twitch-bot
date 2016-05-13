# coding: utf-8
import parser
import socket
import Queue
import thread
import traceback
import time
import json
from time import sleep
from threading import Timer
import atexit
HOST = "irc.twitch.tv"              
PORT = 6667                         
NICK = "squid_coin_bot"            
PASS = "oauth:oju0t5n0yo3cia31ohaz8w9uqv35b2"
CHAN = "drowsysquid75"
class Bot(object):
	def __init__(self, nick, pasw, chan):
		#socket for sending
		self.s = socket.socket()
		#socket for recieving
		self.r = socket.socket()
		#global work queue (comands are queued here)
		self.q = Queue.Queue()
		self.nick = nick
		self.pasw = pasw
		self.chan = chan
		self.commands = {}
		self.chatlog = []
		self.users = {}
		self.timers = []
		self.threads_alive = 1
	def add_user(user, self):
		#add a user to the database
		self.users.update({user.name:user})
	def chat(self, msg):
		#send a chat message using the sending socket
		self.s.send("PRIVMSG #%s : %s\r\n" %(self.chan, msg))
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
		print "connected"
	#commands must run without fail so they tried until they can be appended to the queue
	def command(self, command, mess):
		def command_thread(self, command, mess):
			while self.threads_alive == 1:
				try:
					self.q.put((command, mess))
					break
				except:
					pass
		thread.start_new_thread(command_thread(self, command, mess))
	#start processing queued commands 
	def start_working(self):
		def worker(self):
			while self.threads_alive == 1:
				try:
					command, mess = self.q.get()
					command(mess, self)
				except:
					pass
		thread.start_new_thread(worker, (self,))
	#add a commmand to the list of items to be checked
	def add_command(self, command):
		self.commands.update({command.keyword:command.action})
	def add_timer(self, timer):
		self.timers.append(timer)
	def start_recieving(self):
		def reciever(self):
			while self.threads_alive == 1:
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
			while self.threads_alive == 1:
				try:
					for key in self.commands.keys():
						#makes sure only one command per chat
							if key in self.chatlog[0][1]:
								self.command(self.commands[key], self.chatlog[0][1])
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
		def bot_timer(t, botself):
			t.bot = botself
			t.timer.run()
		for timer in self.timers:
			thread.start_new_thread(bot_timer, (timer,self))
	def start_bot(self):
		self.start_working()
		self.start_recieving()
		self.start_detection()
		self.start_timers()
print "passed"
class command(object):
	def __init__(self, command, bot):
		pass
class timer_ob (object):
	def __init__(self, bot):
		pass
"""
mr = Bot(NICK, PASS, CHAN)
mr.connect(HOST, PORT)
mr.add_command(test())
mr.add_command(schedule_test())
mr.start_bot()
"""
class x(object):
	def __init__(self, bot):
		self.bot = None
	def worker(self):
		print "hello"
		worker(self)
	timer = Timer(worker, 5)
x.timer.run()
mr = Bot(NICK, PASS, CHAN)
mr.add_timer(x)
mr.start_bot()
# coding: utf-8
import parser
import socket
import Queue
import thread
import traceback
HOST = "irc.twitch.tv"              
PORT = 6667                         
NICK = "squid_coin_bot"            
PASS = "oauth:oju0t5n0yo3cia31ohaz8w9uqv35b2"
CHAN = "drowsysquid75"
class Command(object):
	def __init__(self):
		self.keyword = None
	def action(self, message):
		pass
class Bot(object):
	def __init__(self, nick, pasw, chan):
		self.s = socket.socket()
		self.r = socket.socket()
		self.q = Queue.Queue()
		self.nick = nick
		self.pasw = pasw
		self.chan = chan
		self.commands = {}
		self.chatlog = []
	def chat(self, msg):
		self.s.send("PRIVMSG #%s : %s\r\n" %(self.chan, msg))
	def connect(self, host, port):
		self.s.connect((host, port))
		self.s.send("PASS %s\r\n" %self.pasw)
		self.s.send("NICK %s\r\n" %self.nick)
		self.s.send("JOIN %s\r\n" %self.chan)
		self.r.connect((host, port))
		self.r.send("PASS %s\r\n" %self.pasw)
		self.r.send("NICK %s\r\n" %self.nick)
		self.r.send("JOIN %s\r\n" %self.chan)
	def command(self, command, mess):
		while 1:
			try:
				self.q.put((command, mess))
				break
			except:
				pass
	def start_working(self):
		def worker(self):
			while 1:
				try:
					command, mess = self.q.get()
					command(mess)
				except:
					traceback.print_exc()
		thread.start_new_thread(worker, (self,))
	def add_command(self, command):
		self.commands.update({command.keyword:command.action})
	def start_recieving(self):
		def reciever(self):
			while True:
				mess = self.r.recv(2048)
				username = mess.split("!")[1].split("@")[0]
				mess = mess.split(" :")[1]
				self.chatlog.append((username, mess))
	def detection(self):
		def detection_thread(self):
			while True:
				try:
					for key in self.commands.keys():
						if key in self.chatlog[0][1]:
							self.command(self.commands[key], chatlog[0])
							chatlog.remove(chatlog[0])
				except:
					pass
mr = Bot(NICK, PASS, CHAN)
def hi(mess):
	print "%s said %s" % mess
mr.command(hi, ())
mr.start_working()
for x in range(10):
	mr.command(hi, ("hi", "hello"))
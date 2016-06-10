# coding: utf-8
import ui
import thread
class Ui(object):
	def __init__(self, bot):
		self.main = ui.load_view("test")
		self.bot = bot
		self.updates = []
	def update_clock(self):
		def update(self):
			while self.bot.threads_alive:
				for x in range(len(self.updates)):
					self.updates[x]()
				sleep(0.017)
		thread.start_new_thread(update, (self,))
	def add_update(self, update):
		self.updates.append(update)
ui = Ui("test")
ui.update_clock()
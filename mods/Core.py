# coding: utf-8
class give(object):
	def __init__(self):
		self.keyword = "!give "
	def action(self, mess, botself):
		message = mess["message"]
		username = mess["username"]
		if botself.users[username]["is_mod"]:
			_target = message.split(" ")[1]
			_amount = int(message.split(" ")[2])
			botself.users[_target]["currency"] += _amount
			print "%s given %s" % (_target, _amount)
class balance(object):
	def __init__(self):
		self.keyword = "!balance"
	def action(self, mess, botself):
		username = mess["username"]
		botself.chat("%s has %s %s" % (username, botself.users[username]["currency"], currency_name))
class get_time(object):
	def __init__(self):
		self.keyword = "!time"
	def action(self, mess, botself):
		username = mess["username"]
		botself.chat("%s has been online for %sm" % (username, botself.storage["user_time"][username]/60))
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
				if self.bot.users[user]["is_mod"]:
					self.bot.users[user]["is_mod"] = False
			elif user not in self.bot.users.keys():
				self.bot.users.update({user: {"currency" : 0, "is_online": True, "is_mod": False}})
		for user in users_online["moderators"]:
			if user in self.bot.users.keys():
				if self.bot.users[user]["is_online"]:
					pass
				elif not self.bot.users[user]["is_online"]:
					self.bot.users[user]["is_online"] = True
				if not self.bot.users[user]["is_mod"]:
					self.bot.users[user]["is_mod"] = True
			elif user not in self.bot.users.keys():
				self.bot.users.update({user: {"currency" : 0, "is_online": True, "is_mod": True}})
		for user in self.bot.users.keys():
			if user not in users_online["viewers"] + users_online["staff"] + users_online["admins"] + users_online["global_mods"] + users_online["moderators"]:
				self.bot.users[user]["is_online"] = False
		if self.bot.threads_alive:
			x = Timer(1, self.timer)
			thread.start_new_thread(x.run, ())
class handout_currency(object):
	def __init__(self):
		self.bot = None
	name = "handout_currency"
	def timer(self, time, amount):
		for user in self.bot.users:
			if self.bot.users[user]["is_online"]:
				self.bot.users[user]["currency"] += amount
		if self.bot.threads_alive:
			x = Timer(time, self.timer, args=[time, amount])
			thread.start_new_thread(x.run, ())
class time_tracker(object):
	def __init__(self):
		self.bot = None
	name = "time_tracker"
	def timer(self):
		try:
			self.bot.storage["user_time"]
			for user in self.bot.users:
				if user in self.bot.storage["user_time"].keys() and self.bot.users[user]["is_online"]:
					self.bot.storage["user_time"][user] += 1
				elif user not in self.bot.storage["user_time"].keys():
					self.bot.storage["user_time"].update({user: 0})
			x = Timer(1, self.timer)
			thread.start_new_thread(x.run, ())
		except:
			self.bot.storage.update({"user_time": {}})
			x = Timer(1, self.timer)
			thread.start_new_thread(x.run, ())
class auto_save(object):
	def __init__(self):
		self.bot = None
	name = "auto_save"
	def timer(self, time):
		pickle.dump({"storage": self.bot.storage, "users":self.bot.users}, open("save.p", "wb"))
		x = Timer(time, self.timer, args = [time])
		thread.start_new_thread(x.run, ())
bot.add_timer(get_new_users, ())
bot.add_timer(handout_currency, (0.1, 10000))
bot.add_timer(time_tracker, ())
bot.add_timer(auto_save, (60))
bot.add_command(give())
bot.add_command(balance())
bot.add_command(get_time())
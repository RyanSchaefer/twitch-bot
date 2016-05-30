# coding: utf-8
import random
class gambling_slots(object):
	def __init__(self):
		#!slots [amount]
		self.keyword = "!slots "
		self.odds = []
		self.zero = "Kappa"
		self.xhalf = "Keepo"
		self.xone = "ResidentSleeper"
		self.xtwo = "4Head"
		self.xthree = "KAPOW"
		self.xfive = "MingLee"
		self.xten = "ShibeZ"
		self.xhundred = "PogChamp"
		for x in range(1000):
			self.odds.append(self.zero)
		for x in range(500):
			self.odds.append(self.xhalf)
		for x in range(250):
			self.odds.append(self.xone)
		for x in range(125):
			self.odds.append(self.xtwo)
		for x in range(62):
			self.odds.append(self.xthree)
		for x in range(31):
			self.odds.append(self.xfive)
		for x in range(16):
			self.odds.append(self.xten)
		for x in range(8):
			self.odds.append(self.xhundred)
	def action(self, mess, bot):
		try:
			username = mess["username"]
			message = mess["message"]
			amount = int(message.split(" ")[1])
			if bot.users[username]["currency"] >= amount:
				print "test point 1"
				bot.users[username]["currency"] -= amount
				final = []
				multi = 0.0
				print "test point 2"
				for x in range(3):
					final.append(random.choice(self.odds))
				multi += final.count(self.xhalf) * 0.5
				multi += final.count(self.xone) * 1
				multi += final.count(self.xtwo) * 2
				multi += final.count(self.xthree) * 3
				multi += final.count(self.xfive) * 5
				multi += final.count(self.xten) * 10
				multi += final.count(self.xhundred) * 100
				print "test point 3"
				print amount * multi
				bot.chat("The slot machine shows: %s | %s | %s . You won %s%s" % (final[0], final[1], final[2], int(round(amount * multi)), currency_name))
				bot.users[username]["currency"] += int(round(amount * multi))
		except:
			traceback.print_exc()
class gambling_jackpot(object):
	def __init__(self):
		self.keyword = "!jackpot "
	def action(self, mess, bot):
		try:
			username = mess["username"]
			message = mess["message"]
			try:
				jackpot = bot.storage["gambling_jackpot_amount"]
			except:
				bot.storage.update({"gambling_jackpot_amount": 1000000})
				jackpot = 1000000
			amount = int(message.split(" ")[1])
			if bot.users[username]["currency"] >= amount:
				bot.users[username]["currency"] -= amount
				if random.choice(xrange(jackpot)) <= amount:
					bot.chat("PogChamp PogChamp PogChamp %s JUST WON THE JACKPOT! THEY WON %s %s PogChamp PogChamp PogChamp" % (username.upper(), jackpot, currency_name))
					bot.users[username]["currency"] += jackpot
					bot.storage["gambling_jackpot_amount"] = jackpot * 2
					return None
				bot.storage["gambling_jackpot_amount"] += amount
				bot.chat("%s lost %s %s, the jackpot grows to %s" %(username, amount, currency_name, jackpot+amount))
		except:
			traceback.print_exc()
bot.add_command(gambling_slots())
bot.add_command(gambling_jackpot())
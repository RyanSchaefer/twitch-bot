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
		for x in range(100):
			self.odds.append(self.xhalf)
		for x in range(25):
			self.odds.append(self.xone)
		for x in range(15):
			self.odds.append(self.xtwo)
		for x in range(10):
			self.odds.append(self.xthree)
		for x in range(5):
			self.odds.append(self.xfive)
		for x in range(3):
			self.odds.append(self.xten)
		for x in range(1):
			self.odds.append(self.xhundred)
	def action(self, mess, bot):
		try:
			username = mess["username"]
			message = mess["message"]
			amount = int(message.split(" ")[1])
			if bot.users[username]["currency"] >= amount:
				bot.users[username]["currency"] -= amount
				final = []
				multi = 0.0
				for x in range(3):
					final.append(random.choice(self.odds))
				multi += final.count(self.xhalf) * 0.5
				multi += final.count(self.xone) * 1
				multi += final.count(self.xtwo) * 2
				multi += final.count(self.xthree) * 3
				multi += final.count(self.xfive) * 5
				multi += final.count(self.xten) * 10
				multi += final.count(self.xhundred) * 100
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
class gambling_break_the_bank(object):
	def __init__(self):
		self.keyword = "!btb "
	def action(self, mess, bot):
		pass
class gambling_bet_pool_bet(object):
	def __init__(self):
		self.keyword = "!bet "
	def action(self, mess, bot):
		try:
			username = mess["username"]
			message = mess["message"]
			bet = int(message.split(" ")[2])
			choice = message.split(" ")[1]
			if bot.users[username]["currency"] >= bet and bot.storage["gambling_bet_pool"]["is_open"] and (choice == "1" or choice == "2"):
				bot.users[username]["currency"] -= bet
				bot.storage["gambling_bet_pool"]["pot"] += bet
				bot.storage["gambling_bet_pool"]["users"].update({username:{"bet":bet,"choice":choice}})
				bot.storage["gambling_bet_pool"]["choice"+choice] += bet
				bot.chat("A bet of %s has been placed on %s by %s" % (bet, choice, username))
		except:
			traceback.print_exc()
class gambling_bet_pool_open(object):
	def __init__(self):
		self.keyword = "!openpool"
	def action(self, mess, bot):
		username = mess["username"]
		if bot.users[username]["is_mod"]:
			try:
				bot.storage["gambling_bet_pool"]["is_open"] = True
			except:
				bot.storage.update({"gambling_bet_pool":{"choice1":0,"choice2":0,"pot":0,"is_open":True,"users":{}}})
		bot.chat("A pool has been opened!")
class gambling_bet_pool_close(object):
	def __init__(self):
		self.keyword = "!closepool "
	def action(self, mess, bot):
		try:
			username = mess["username"]
			message = mess["message"]
			winner = message.split(" ")[1]
			if bot.users[username]["is_mod"]:
				if winner == "rng":
					winner = str(random.randint(1,2))
				try:
					odds_for_winner = float(bot.storage["gambling_bet_pool"]["pot"]) / float(bot.storage["gambling_bet_pool"]["choice"+winner])
				except:
					odds_for_winner = 0
				bot.storage["gambling_bet_pool"]["is_open"] = False
				bets = bot.storage["gambling_bet_pool"]["users"]
				pot = bot.storage["gambling_bet_pool"]["pot"]
				for user in bets:
					if bets[user]["choice"] == winner:
						bot.users[user]["currency"] += int(round(bets[user]["bet"] * odds_for_winner)) + bets[user]["bet"]
				bot.storage["gambling_bet_pool"]["choice1"] = 0
				bot.storage["gambling_bet_pool"]["choice2"] = 0
				bot.storage["gambling_bet_pool"]["pot"] = 0
				bot.storage["gambling_bet_pool"]["users"] = {}
			bot.chat("A pool has been closed with option%s as the winner. %s %s has been handed out to winners." % (winner, pot, currency_name))
		except:
			traceback.print_exc()
class gambling_roulette(object):
	def __init__(self):
		self.keyword = "!r "
		self.bot = None
		self.black_numbers = [2, 4, 6, 8, 10, 11,13, 15, 17, 20, 22, 24,26, 28, 29, 31, 33, 35]
		self.red_numbers = [1, 3, 5, 7, 9, 12,14, 16, 18, 19, 21, 23,25, 27, 30, 32, 34, 36]
		self.evens = range(37)[2::2]
		self.odds = range(37)[1::2]
		self.closing = False
	def alert_half(self):
		self.bot.chat("The roulette ball rattles...")
		Timer(15, self.close).run()
	def close(self):
		self.closing = True
		self.bot.chat("All bets final! The ball is dropping...")
		bets = self.bot.storage["gambling_roulette"]["bets"]
		winner = random.randint(0,36)
		for user in bets:
			for number in bets[user][number]:
				if number == winner:
					self.bot.users[user]["currency"] += bets[user]["bet"]*35
				if number == "red":
					if winner in self.red_numbers:
						self.bot.users[user]["currency"] += bets[user]["bet"]*2
				if number == "black":
					if winner in self.black_numbers:
						self.bot.users[user]["currency"] += bets[user]["bet"]*2
				if number == "odds":
					if winner in self.odds:
						self.bot.users[user]["currency"] += bets[user]["bet"]*2
				if number == "evens":
					if winner in self.evens:
						self.bot.users[user]["currency"] += bets[user]["bet"]*2
		self.bot.storage["gambling_roulette"]["bets"] = {}
		self.bot.storage["gambling_roulette"]["is_open"] = False
		self.closing = False
		time.sleep(3)
		print "running final chat message"
		self.bot.chat("The winning number was... %s! Congrats to all who played" % (winner))
	def action(self, mess, bot):
		try:
			self.bot = bot
			message = mess["message"]
			numbers = message.split(" ")[1].replace(" ", "").split(",")
			bet = int(message.split(" ")[2])
			username = mess["username"]
			if len(numbers) * bet <= bot.users[username]["currency"] and not self.closing:
				bot.users[username]["currency"] -= bet * len(numbers)
				try:
					if not bot.storage["gambling_roulette"]["is_open"]:
						bot.storage["gambling_roulette"]["is_open"] = True
						bot.chat("A round of roulette has started. Join by saying !r [list of numbers 0-36, black, red, evens, or odds] [bet for each].")
						Timer(15, self.alert_half).run()
				except:
					bot.chat("A round of roulette has started. Join by saying !r [list of numbers 0-36, black, red, evens, or odds] [bet for each].")
					bot.storage.update({"gambling_roulette":{"is_open":True, "bets": {}}})
					Timer(15, self.alert_half).run()
				if username in bot.storage["gambling_roulette"]["bets"]:
					bot.users[username]["currency"] += len(bot.storage["gambling_roulette"]["bets"][username]["numbers"]) * bot.storage["gambling_roulette"]["bets"][username]["bet"]
					del bot.storage["gambling_roulette"]["bets"][username]
				if bot.storage["gambling_roulette"]["is_open"] and username not in bot.storage["gambling_roulette"]["bets"]:
					bot.storage["gambling_roulette"]["bets"].update({username:{"bet":bet, "numbers":None}})
					valid_numbers = []
					for number in numbers:
						try:
							valid_numbers.append(int(number))
						except:
							if number == "red" or number == "black" or number == "odds" or number == "evens":
								valid_numbers.append(number)
							if number == "fix" and bot.users[username]["is_mod"]:
								for user in bot.storage["gambling_roulette"]["bets"]:
									bot.users[user]["currency"] += bot.storage["gambling_roulette"]["bets"][user]["bet"] * len(bot.storage["gambling_roulette"]["bets"][user]["numbers"])
					bot.storage["gambling_roulette"]["bets"][username]["numbers"] = valid_numbers
		except:
			traceback.print_exc()

bot.add_command(gambling_slots())
bot.add_command(gambling_jackpot())
bot.add_command(gambling_bet_pool_bet())
bot.add_command(gambling_bet_pool_open())
bot.add_command(gambling_bet_pool_close())
bot.add_command(gambling_roulette())
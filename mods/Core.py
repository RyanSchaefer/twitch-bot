class CoreHandOutCurrency(object):
    def __init__(self, bot, amount, time):
        self.amount = amount
        self.time = time
        self.bot = bot
    def start(self):
        def working(self):
            if self.bot.threads_alive:
                for user in self.bot.users:
                    if self.bot.users[user].is_online:
                        self.bot.bot_give(self.bot,user, self.amount)
              t = Timer(self.time, working, kwargs={"self":self})
              start_new_thread(t.start, ())
class CoreGetCurrency(object):
    
bot.timers.update("CoreHandOutCurrency": CoreHandOutCurrency(bot, 1, 1))
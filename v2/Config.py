import configparser

class Config():

    def __init__(self):
        self.cp = configparser.ConfigParser()
    
    def reloadConfig(self, base):
        self.cp.read("config.cfg")
        self.quantity = self.cp.getfloat(base, "quantity")
        self.minstep = self.cp.getfloat(base, "minstep")
        self.profit = self.cp.getfloat(base, "profit")
        self.exit = self.cp.getboolean("MAIN", "exit")
        self.API_KEY = self.cp.get("MAIN", "API_KEY")
        self.API_SECRET = self.cp.get("MAIN", "API_SECRET")

i = Config()
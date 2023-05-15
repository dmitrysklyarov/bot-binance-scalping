import configparser

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config/config.ini')

    def get(self, section, option):
        return self.config.get(section, option)
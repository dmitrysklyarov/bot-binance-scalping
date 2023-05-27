import configparser

def _get_config():
    config = configparser.ConfigParser()
    return config.read('config.ini')

from functions import get_config


class Switch(object):
    def __init__(self, name):
        self.name = name
        self.config = get_config()['devices'][name]
        self.ip = self.config['IP']

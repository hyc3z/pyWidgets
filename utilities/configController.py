
import configparser
import os

class configController:

    def __init__(self):
        self.config = configparser.ConfigParser()

    def get_config(self, path):
        self.config.read(path)
        for i in self.config.items():
            print(i)

    def write_config(self, path):
        with open(path, 'w') as configfile:
            self.config.write(configfile)

    def current_config(self):
        return self.config


if __name__ == '__main__':
    cc = configController()
    config = cc.current_config()
    config['add'] = {'True':'True'}
    cc.write_config("user.conf")

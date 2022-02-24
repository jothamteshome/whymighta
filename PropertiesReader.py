import configparser


# Reads in keys from keys.properties file
class PropertiesReader:
    def __init__(self):
        self.__config_parser = configparser.ConfigParser()
        self.__config_parser.read('keys.properties')

    def get(self, key):
        return self.__config_parser.get('keys', key)

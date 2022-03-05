import configparser


# Reads from important_info.properties file
class PropertiesReader:
    def __init__(self):
        self.__config_parser = configparser.ConfigParser()
        self.__config_parser.read('Resources/important_info.properties')

    # Get key from important_info.properties file
    def get_key(self, key):
        return self.__config_parser.get('keys', key)

    # Get name from important_info.properties file
    def get_name(self, identifier):
        return self.__config_parser.get('names', identifier)

    # Open a file with a name stored in important_info.properties file
    def open(self, file, version):
        return open("Resources/" + self.__config_parser.get('files', file.upper()), version)


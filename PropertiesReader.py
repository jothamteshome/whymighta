import configparser


# Reads from important_info.properties file
class PropertiesReader:
    def __init__(self):
        self.__config_parser = configparser.ConfigParser()
        self.__config_parser.read('Resources/important_info.properties')

    # Get key from important_info.properties file
    def getDatabaseInfo(self, identifier):
        return self.__config_parser.get('database_info', identifier)



import configparser
import os


def load_config(config_file=None):
    if config_file is None:
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")

    config = configparser.ConfigParser()
    config.read(config_file)
    return config


config = load_config()


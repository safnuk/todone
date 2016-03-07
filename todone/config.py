import configparser
import os

VERSION = '0.01'
DEFAULT_CONFIG_FILE = '~/.config/todone/config.ini'

settings = {
    'database': {
        'type': 'sqlite3',
        'name': '',
    },
}


def configure(config_file):
    config_file = config_file if config_file else DEFAULT_CONFIG_FILE
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(config_file))
    for key in config.sections():
        if key in settings:
            settings[key].update(config[key])
        else:
            settings[key] = dict(config[key])

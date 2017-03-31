import configparser
import os

DEFAULT_CONFIG_FILE = '~/.config/todone/config.ini'

config_file = DEFAULT_CONFIG_FILE
settings = {
    'database': {
        'type': 'sqlite3',
        'name': '',
    },
}


def configure(filename):
    globals()['config_file'] = filename if filename else DEFAULT_CONFIG_FILE
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(config_file))
    for key in config.sections():
        if key in settings:
            settings[key].update(config[key])
        else:
            settings[key] = dict(config[key])


def save_configuration():
    config = configparser.ConfigParser()
    config.read_dict(settings)
    filename = os.path.expanduser(config_file)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as configfile:
        config.write(configfile)


class ConfigurationError(Exception):
    pass

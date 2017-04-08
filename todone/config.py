"""Handle global configuration settings for use by other modules in todone.

Includes:
    :data:`settings` Dictionary of global configuration settings.
    :func:`configure` Read configuration settings from disk.
    :func:`save_configuration` Save configuration settings to disk.
"""
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
    """Read configuration settngs from disk.

    If :data:`filename` is the empty string, use default configuration
    settings.

    :param filename: Location of config file on disk.
    """
    globals()['config_file'] = filename if filename else DEFAULT_CONFIG_FILE
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(config_file))
    for key in config.sections():
        if key in settings:
            settings[key].update(config[key])
        else:
            settings[key] = dict(config[key])


def save_configuration():
    """Save configuration settings to the file :data:`config.config_file`."""
    config = configparser.ConfigParser()
    config.read_dict(settings)
    filename = os.path.expanduser(config_file)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as configfile:
        config.write(configfile)


class ConfigurationError(Exception):
    pass

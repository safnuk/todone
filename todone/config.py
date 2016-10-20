import configparser
import os

VERSION = '0.01'
DEFAULT_CONFIG_FILE = '~/.config/todone/config.ini'

settings = {
    'database': {
        'type': 'sqlite3',
        'name': '',
    },
    'folders': {
        'default_inbox': 'inbox',
        'default_folders': [
            'today', 'next', 'inbox', 'cal',
            'done', 'someday'
        ],
        'active': ['today', 'next', 'inbox'],
        'inactive': ['done', 'cancel'],
        'cal': ['cal'],
        'today': ['today'],
        'do_not_archive': ['cancel'],
    },
}

_folder_lists = [
    'default_folders', 'active', 'cal', 'today', 'do_not_archive',
    'inactive',
]


def configure(config_file):
    config_file = config_file if config_file else DEFAULT_CONFIG_FILE
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(config_file))
    for key in config.sections():
        if key == 'folders':
            temp_folders = dict(config[key])
            for sub_key, value in temp_folders.items():
                if sub_key in _folder_lists:
                    temp_folders[sub_key] = [
                        x.strip() for x in value.split(',')
                    ]
            settings[key].update(temp_folders)
        elif key in settings:
            settings[key].update(config[key])
        else:
            settings[key] = dict(config[key])

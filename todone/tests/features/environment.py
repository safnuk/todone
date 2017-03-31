TEST_DB = 'todone/tests/test.sqlite3'
BLANK_CONFIG_FILE = 'todone/tests/blank_config.ini'


def before_scenario(context, scenario):
    context.output = ""
    # clear test database
    with open(TEST_DB, 'w'):
        pass
    # clear blank config file
    with open(BLANK_CONFIG_FILE, 'w'):
        pass


def before_feature(context, feature):
    context.test = feature.filename


def after_feature(context, feature):
    del context.test

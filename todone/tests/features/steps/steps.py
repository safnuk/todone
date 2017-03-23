from contextlib import redirect_stdout
import io

from behave import *
from hamcrest import *

from todone.application import main

CONFIG_DB = ['-c', 'todone/tests/config_db.ini']


def run_todone(args):
    return run_todone_with_config(args, CONFIG_DB)


def run_todone_with_config(args, config):
    f = io.StringIO()
    with redirect_stdout(f):
        main(config + args)
    return f.getvalue()


@given('an initialized database')
def step_impl(context):
    run_todone(['setup', 'init'])


@then('the output includes "{text}"')
def step_impl(context, text):
    assert_that(context.output, contains_string(text))


@then('the output includes each <{column}>')
def step_impl(context, column):
    for row in context.table:
        entry = row[column]
        context.execute_steps('then the output includes "{}"'.format(entry))


@then('the output does not include "{text}"')
def step_impl(context, text):
    assert_that(context.output, not_(contains_string(text)))


@when('we add a new todo item')
def step_impl(context):
    context.output += run_todone(['new', 'New todo item'])


@when('we list the folders')
def step_impl(context):
    context.output += run_todone(['folder', 'list'])


@when('we initialize the database')
def step_impl(context):
    context.output += run_todone(['setup', 'init'])


@given('an unitialized database')
def step_impl(context):
    pass

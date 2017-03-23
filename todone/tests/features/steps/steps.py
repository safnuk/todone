from contextlib import redirect_stdout
import io

from behave import given, when, then
from hamcrest import assert_that, contains_string, not_

from todone.application import main

CONFIG_DB = ['-c', 'todone/tests/config_db.ini']


def run_todone(args):
    return run_todone_with_config(args, CONFIG_DB)


def run_todone_with_config(args, config):
    f = io.StringIO()
    with redirect_stdout(f):
        main(config + args)
    return f.getvalue()


@given('an existing todo "{todo}"')
def step_impl(context, todo):
    run_todone(['new', todo])


@given('we ran the command "{command}"')
def step_impl(context, command):
    args = command.split(' ')
    run_todone(args)


@given('the database includes each <todo>')
def step_impl(context):
    for row in context.table:
        entry = row['todo']
        run_todone(['new', entry])


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


@when('we run the command "{command}"')
def step_impl(context, command):
    args = command.split(' ')
    context.output += run_todone(args)


@when('we run each of the commands <command>')
def step_impl(context):
    for row in context.table:
        entry = row['command']
        context.execute_steps('when we run the command "{}"'.format(entry))


@given('an unitialized database')
def step_impl(context):
    pass

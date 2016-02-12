import datetime
import pytest

from ..todo import Todo

def test_class_is_importable():
    t = Todo('Blank')
    assert(type(t) == Todo)

def test_todo_stores_action():
    t = Todo('New todo item')
    assert(t.action == 'New todo item')

def test_todo_raises_with_empty_action():
    with pytest.raises(ValueError) as context:
        t = Todo('')

def test_todo_stores_valid_type():
    for _type in [x for x in Todo.TYPES if x != Todo.REMIND]:
        t = Todo('Test todo', _type=_type)
        assert(t._type == _type)

def test_todo_default_type_is_inbox():
    t = Todo('Test')
    assert(t._type == Todo.INBOX)

def test_todo_raises_with_invalid_type():
    with pytest.raises(ValueError) as context:
        t = Todo('Test', _type='invalid')

def test_remind_todos_store_date():
    today = datetime.date.today()
    t = Todo('Test', _type=Todo.REMIND, remind_date=today)
    assert(t.remind_date == today)

def test_non_remind_todos_do_not_store_remind_date():
    t = Todo('Test')
    with pytest.raises(AttributeError) as context:
        assert(t.remind_date == None)

def test_remind_items_withtout_date_raises():
    with pytest.raises(ValueError) as context:
        t = Todo('Test', _type=Todo.REMIND)

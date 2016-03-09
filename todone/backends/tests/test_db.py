from unittest import skip

import peewee

from todone.backends.db import ListItem, SavedList, Todo, MOST_RECENT_SEARCH
from todone.config import settings
from todone.tests.base import DB_Backend


class TestTodoModel(DB_Backend):

    def test_class_is_importable(self):
        t = Todo(action='Blank')
        self.assertEqual(type(t), Todo)

    def test_todo_stores_action(self):
        t = Todo(action='New todo item')
        self.assertEqual(t.action, 'New todo item')
        t.save()

    def test_todo_raises_with_empty_action(self):
        with self.assertRaises(peewee.IntegrityError):
            t = Todo(action='')
            t.save()

    def test_todo_stores_valid_folder(self):
        for folder in [x for x in settings['folders']['default_folders']]:
            t = Todo(action='Test todo', folder=folder)
            t.save()
            self.assertEqual(t.folder, folder)

    def test_todo_default_folder_is_inbox(self):
        t = Todo(action='Test')
        t.save()
        self.assertEqual(t.folder, settings['folders']['default_inbox'])

    def test_active_todos_restricts_select(self):
        todos = {}
        for n, folder in enumerate(settings['folders']['default_folders']):
            todos[folder] = Todo.create(
                action='Item {}'.format(n), folder=folder
            )
        active = Todo.active_todos()
        active_todos = [t for t in active]

        test_active = settings['folders']['active']
        test_inactive = [
            x for x in settings['folders']['default_folders']
            if x not in test_active
        ]
        for folder in test_inactive:
            self.assertNotIn(todos[folder], active_todos)
        for folder in test_active:
            self.assertIn(todos[folder], active_todos)

    @skip
    def test_todo_raises_with_invalid_folder(self):
        with self.assertRaises(ValueError):
            t = Todo(action='Test', folder='invalid')
            t.save()


class TestSavedList(DB_Backend):

    def test_class_is_importable(self):
        t = SavedList(name='test')
        self.assertEqual(type(t), SavedList)

    def test_savedlist_raises_with_empty_name(self):
        with self.assertRaises(peewee.IntegrityError):
            SavedList.create(name='')

    def test_raises_with_duplicate_name(self):
        SavedList.create(name='test')
        with self.assertRaises(peewee.IntegrityError):
            SavedList.create(name='test')

    def test_get_most_recent_does_as_advertised(self):
        s1 = SavedList.get_most_recent()
        self.assertEqual(s1.name, MOST_RECENT_SEARCH)
        s2 = SavedList.get_most_recent()
        self.assertEqual(s2.name, MOST_RECENT_SEARCH)

    def test_get_todos_in_list_returns_empty_list_if_list_not_exists(self):
        s = SavedList.create(name='test')
        t = Todo.create(action='Test todo')
        ListItem.create(savedlist=s, todo=t)
        self.assertEqual(SavedList.get_todos_in_list('foo'), [])

    def test_get_todos_in_list_returns_list_todos(self):
        s = SavedList.create(name='test')
        t1 = Todo.create(action='Test todo')
        t2 = Todo.create(action='Test another todo')
        ListItem.create(savedlist=s, todo=t1)
        ListItem.create(savedlist=s, todo=t2)
        self.assertEqual(SavedList.get_todos_in_list('test'), [t1, t2])

    def test_get_todos_in_list_defaults_to_MOST_RECENT_SEARCH(self):
        s1 = SavedList.create(name='test')
        s2 = SavedList.create(name=MOST_RECENT_SEARCH)
        t1 = Todo.create(action='Test todo')
        t2 = Todo.create(action='Test another todo')
        ListItem.create(savedlist=s1, todo=t1)
        ListItem.create(savedlist=s2, todo=t2)
        self.assertEqual(SavedList.get_todos_in_list(''), [t2])

    def test_delete_items_erases_all_items_in_list(self):
        s = SavedList.create(name='test')
        t1 = Todo.create(action='Test todo')
        t2 = Todo.create(action='Test another todo')
        ListItem.create(savedlist=s, todo=t1)
        ListItem.create(savedlist=s, todo=t2)
        s.delete_items()
        self.assertEqual(SavedList.get_todos_in_list('test'), [])

    def test_save_most_recent_search_clears_old_items(self):
        s = SavedList.create(name=MOST_RECENT_SEARCH)
        t1 = Todo.create(action='Test todo')
        t2 = Todo.create(action='Test another todo')
        ListItem.create(savedlist=s, todo=t1)
        SavedList.save_most_recent_search([t2])
        self.assertNotIn(t1, SavedList.get_todos_in_list(MOST_RECENT_SEARCH))

    def test_save_most_recent_search_saves_all_passed_todos(self):
        t1 = Todo.create(action='Test todo')
        t2 = Todo.create(action='Test another todo')
        SavedList.save_most_recent_search([t1, t2])
        self.assertEqual(
            SavedList.get_todos_in_list(MOST_RECENT_SEARCH), [t1, t2])


class TestListItem(DB_Backend):

    def test_raises_without_list(self):
        t = Todo.create(action='Test todo')
        with self.assertRaises(peewee.IntegrityError):
            ListItem.create(todo=t)

    def test_raises_without_todo(self):
        l = SavedList.create(name='List')
        with self.assertRaises(peewee.IntegrityError):
            ListItem.create(savedlist=l)

    def test_listitems_ordered_by_insertion_order(self):
        l = SavedList.create(name='List')
        todos = []
        todos.append(Todo.create(action='Todo 1'))
        todos.append(Todo.create(action='Another todo'))
        todos.append(Todo.create(action='Random todo', folder='today'))
        ListItem.create(savedlist=l, todo=todos[0])
        ListItem.create(savedlist=l, todo=todos[1])
        ListItem.create(savedlist=l, todo=todos[2])
        items = ListItem.select().where(ListItem.savedlist == l)
        pairs = zip(items, todos)
        for item, todo in pairs:
            self.assertEqual(item.todo, todo)

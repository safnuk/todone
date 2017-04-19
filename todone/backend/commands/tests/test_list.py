from contextlib import redirect_stdout
from datetime import date, timedelta
import io
from unittest import skip, TestCase
from unittest.mock import patch

from todone.backend import (
    DEFAULT_FOLDERS,
)
from todone.backend.db import ListItem, MOST_RECENT_SEARCH, SavedList, Todo
from todone.backend.commands.list import (
    is_loading_saved_search,
    list_items,
)
from todone.tests.base import DB_Backend

folders = DEFAULT_FOLDERS['folders']


class TestListItems(DB_Backend):

    def test_list_folder_restricts_to_correct_todos(self):
        todos = {}
        for n, folder in enumerate(folders):
            todos[folder] = Todo.create(
                action='Item {}'.format(n), folder=folder
            )
        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['today/'])
        s = f.getvalue()
        for folder in [
            x for x in folders if x is not 'today'
        ]:
            self.assertNotIn(str(todos[folder]), s)
        self.assertIn(str(todos['today']), s)

        for list_folder in folders:
            f = io.StringIO()
            with redirect_stdout(f):
                list_items([list_folder + '/'])
            s = f.getvalue()
            for folder in [
                x for x in folders
                if x is not list_folder
            ]:
                self.assertNotIn(str(todos[folder]), s)
            self.assertIn(str(todos[list_folder]), s)

    def test_list_without_folder_restricts_to_active_todos(self):
        todos = {}
        for n, folder in enumerate(folders):
            todos[folder] = Todo.create(
                action='Item {}'.format(n), folder=folder
            )
        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['Item'])
        s = f.getvalue()
        active = DEFAULT_FOLDERS['active']
        inactive = [x for x in folders if x not in active]
        for folder in inactive:
            self.assertNotIn(str(todos[folder]), s)
        for folder in active:
            self.assertIn(str(todos[folder]), s)

    def test_list_restricts_by_search_keywords(self):
        t1 = Todo.create(
            action='Test todo with search',
            folder='inbox'
        )
        t2 = Todo.create(
            action='Test todo with grok',
            folder='inbox'
        )
        t3 = Todo.create(
            action='Search todo for foo',
            folder='today'
        )

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['grok'])
        s = f.getvalue()
        self.assertNotIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertNotIn(str(t3), s)

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['inbox/', 'test todo', 'with'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertNotIn(str(t3), s)

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['test'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertNotIn(str(t3), s)

    def test_list_restricts_by_duedate(self):
        t1 = Todo.create(
            action='Test 1',
            folder='inbox',
            due=date.today()
        )
        t2 = Todo.create(
            action='Foo 2',
            folder='next',
            remind=date.today(),
            due=date.today() + timedelta(days=10)
        )
        t3 = Todo.create(
            action='Grok 3',
            folder='today',
            due=date.today() - timedelta(days=2)
        )
        t4 = Todo.create(
            action='Sublime 4',
            folder='next',
            due=date.today() + timedelta(days=20)
        )
        t5 = Todo.create(
            action='Sublime 5',
            folder='next',
        )
        t6 = Todo.create(
            action='Sublime 6',
            folder='done',
            due=date.today()
        )

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['due'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['due+15d'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertNotIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['due+0d'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertNotIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertNotIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['due+3m'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)

    def test_list_restricts_by_remind_date(self):
        t1 = Todo.create(
            action='Test 1',
            folder='inbox',
            remind=date.today()
        )
        t2 = Todo.create(
            action='Foo 2',
            folder='next',
            due=date.today(),
            remind=date.today() + timedelta(days=10)
        )
        t3 = Todo.create(
            action='Grok 3',
            folder='today',
            remind=date.today() - timedelta(days=2)
        )
        t4 = Todo.create(
            action='Sublime 4',
            folder='next',
            remind=date.today() + timedelta(days=20)
        )
        t5 = Todo.create(
            action='Sublime 5',
            folder='next',
        )
        t6 = Todo.create(
            action='Sublime 6',
            folder='done',
            remind=date.today()
        )

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['remind'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['remind+15d'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertNotIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['remind+0d'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertNotIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertNotIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['remind+3m'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)

    @skip
    def test_list_restricts_by_cal_date(self):
        self.fail("Write this test!")

    def test_list_restricts_by_parent(self):
        project = Todo.create(
            action='Project',
            folder='next'
        )
        t1 = Todo.create(
            action='Test todo with search',
            folder='inbox',
            parent=project
        )
        t2 = Todo.create(
            action='Test todo with grok',
            folder='inbox'
        )
        t3 = Todo.create(
            action='Search todo for foo',
            folder='today',
            parent=project
        )

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['[project]'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertNotIn(str(t2), s)
        self.assertIn(str(t3), s)

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['[next/project]'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertNotIn(str(t2), s)
        self.assertIn(str(t3), s)

    def test_list_saves_last_search(self):
        Todo.create(
            action='Test todo with search',
            folder='inbox'
        )
        t2 = Todo.create(
            action='Test todo with grok',
            folder='inbox'
        )
        Todo.create(
            action='Search todo for foo',
            folder='today'
        )
        list_items(['grok'])
        saved = SavedList.get(name=MOST_RECENT_SEARCH)
        items = ListItem.select().where(ListItem.savedlist == saved)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].todo, t2)

    def test_list_without_args_uses_last_search(self):
        t1 = Todo.create(
            action='Test todo with search',
            folder='inbox'
        )
        t2 = Todo.create(
            action='Test todo with grok',
            folder='inbox'
        )
        t3 = Todo.create(
            action='Search todo for foo',
            folder='today'
        )
        recent = SavedList.get_most_recent()
        ListItem.create(savedlist=recent, todo=t1)
        ListItem.create(savedlist=recent, todo=t2)
        f = io.StringIO()
        with redirect_stdout(f):
            list_items([])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertNotIn(str(t3), s)

    def test_list_parent_displays_all_subtodos_for_parent(self):
        project = Todo.create(
            action='project',
            folder='next'
        )
        t1 = Todo.create(
            action='Test todo with search',
            folder='inbox',
            parent=project
        )
        t2 = Todo.create(
            action='Test todo with grok',
            folder='inbox'
        )
        t3 = Todo.create(
            action='Search todo for foo',
            folder='today',
            parent=project
        )
        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['[project]'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertNotIn(str(t2), s)
        self.assertIn(str(t3), s)

    def test_order_by_project(self):
        project1 = Todo.create(
            action='A project',
            folder='next'
        )
        project2 = Todo.create(
            action='B project',
            folder='next'
        )
        t1 = Todo.create(
            action='Test todo with search',
            folder='today',
            parent=project2
        )
        t2 = Todo.create(
            action='Test todo with grok',
            folder='today',
            parent=project1
        )
        t3 = Todo.create(
            action='Search todo for foo',
            folder='today',
        )

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['today/'])
        s = f.getvalue()
        lines = s.split('\n')
        self.assertIn(str(t3), lines[0])
        self.assertIn(project1.action, lines[1])
        self.assertIn(str(t2), lines[2])
        self.assertIn(project2.action, lines[3])
        self.assertIn(str(t1), lines[4])


@patch('todone.parser.commands.list.parse_args')
@patch('todone.commands.list.is_loading_saved_search')
class UnitTestListItems(TestCase):

    def setUp(self):
        self.parsed_args = {
            'file': 'test',
            'folder': None,
            'parent': None,
        }

    @patch('todone.commands.list.backend.SavedList')
    def test_if_loading_saved_search_then_calls_loader(
        self, MockSavedList, mock_is_loading, mock_parse
    ):
        mock_parse.return_value = self.parsed_args
        mock_is_loading.return_value = True
        list_items([])
        MockSavedList.get_todos_in_list.assert_called_once_with(
            self.parsed_args['file'])

    @patch('todone.commands.list.backend.SavedList')
    def test_if_loading_saved_search_then_does_not_saves_query(
        self, MockSavedList, mock_is_loading, mock_parse
    ):
        mock_parse.return_value = self.parsed_args
        mock_is_loading.return_value = True
        list_items([])
        MockSavedList.save_search.assert_not_called()

    @patch('todone.commands.list.backend.SavedList')
    @patch('todone.commands.list.printers.print_todo_list')
    def test_if_loading_saved_search_then_saves_as_most_recent_query(
        self, mock_print, MockSavedList, mock_is_loading, mock_parse
    ):
        mock_parse.return_value = self.parsed_args
        mock_is_loading.return_value = True
        MockSavedList.get_todos_in_list.return_value = 'test'
        list_items([])
        MockSavedList.save_most_recent_search.assert_called_once_with('test')

    @patch('todone.commands.list.backend.Todo.query')
    @patch('todone.commands.list.backend.SavedList')
    def test_if_not_loading_saved_search_then_constructs_query(
        self, MockSavedList, mock_construct, mock_is_loading, mock_parse
    ):
        mock_parse.return_value = self.parsed_args
        mock_is_loading.return_value = False
        list_items([])
        mock_construct.assert_called_once_with(**self.parsed_args)

    @patch('todone.commands.list.backend.Todo.query')
    @patch('todone.commands.list.backend.SavedList')
    @patch('todone.commands.list.printers.print_todo_list')
    def test_if_not_loading_saved_search_then_saves_query(
        self, mock_print, MockSavedList, mock_construct,
        mock_is_loading, mock_parse
    ):
        mock_parse.return_value = self.parsed_args
        mock_is_loading.return_value = False
        mock_construct.return_value = 'test todo'
        list_items([])
        MockSavedList.save_search.assert_called_once_with(
            self.parsed_args['file'], 'test todo')

    @patch('todone.commands.list.backend.Todo.query')
    @patch('todone.commands.list.backend.SavedList')
    @patch('todone.commands.list.printers.print_todo_list')
    def test_if_not_loading_saved_search_then_saves_as_most_recent_query(
        self, mock_print, MockSavedList, mock_construct,
        mock_is_loading, mock_parse
    ):
        mock_parse.return_value = self.parsed_args
        mock_is_loading.return_value = False
        mock_construct.return_value = 'test todo'
        list_items([])
        MockSavedList.save_most_recent_search.assert_called_once_with(
            'test todo')


class TestIsLoading(TestCase):
    def test_empty_dict_arg_returns_True(self):
        self.assertTrue(is_loading_saved_search({}))

    def test_dict_with_all_false_values_return_True(self):
        test = {
            'key1': None,
            'key2': [],
            'key3': ''
        }
        self.assertTrue(is_loading_saved_search(test))

    def test_dict_with_a_true_value_returns_False(self):
        test = {
            'key1': None,
            'key2': True,
            'key3': ''
        }
        self.assertFalse(is_loading_saved_search(test))

    def test_dict_with_only_non_false_being_file_returns_True(self):
        test = {
            'file': 'test',
            'key1': None,
            'key2': [],
            'key3': ''
        }
        self.assertTrue(is_loading_saved_search(test))

from datetime import date, timedelta
from unittest import skip, TestCase
from unittest.mock import patch

from todone.backend import DEFAULT_FOLDERS
from todone.backend.db import ListItem, MOST_RECENT_SEARCH, SavedList, Todo
from todone.backend.commands import List
from todone.tests.base import DB_Backend

folders = DEFAULT_FOLDERS['folders']


class TestListItems(DB_Backend):

    def test_list_folder_restricts_to_correct_todos(self):
        todos = {}
        for n, folder in enumerate(folders):
            todos[folder] = Todo.create(
                action='Item {}'.format(n), folder=folder
            )
        s, r = List.run({'folder': 'to'})
        self.assertEqual(s, 'todo_query')
        for folder in [
            x for x in folders if x is not 'today'
        ]:
            self.assertNotIn(todos[folder], r)
        self.assertIn(todos['today'], r)

        for list_folder in folders:
            s, r = List.run({'folder': list_folder})
            for folder in [
                x for x in folders
                if x is not list_folder
            ]:
                self.assertNotIn(todos[folder], r)
            self.assertIn(todos[list_folder], r)

    def test_list_without_folder_restricts_to_active_todos(self):
        todos = {}
        for n, folder in enumerate(folders):
            todos[folder] = Todo.create(
                action='Item {}'.format(n), folder=folder
            )
        s, r = List.run({'keywords': ['Item']})
        active = DEFAULT_FOLDERS['active']
        inactive = [x for x in folders if x not in active]
        for folder in inactive:
            self.assertNotIn(todos[folder], r)
        for folder in active:
            self.assertIn(todos[folder], r)

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

        s, r = List.run({'keywords': ['grok']})
        self.assertNotIn(t1, r)
        self.assertIn(t2, r)
        self.assertNotIn(t3, r)

        s, r = List.run({'folder': 'inbox', 'keywords': ['test todo', 'with']})
        self.assertIn(t1, r)
        self.assertIn(t2, r)
        self.assertNotIn(t3, r)

        s, r = List.run({'keywords': ['test']})
        self.assertIn(t1, r)
        self.assertIn(t2, r)
        self.assertNotIn(t3, r)

    @skip
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

        s, r = List.run(['due'])
        self.assertIn(t1, r)
        self.assertIn(t2, r)
        self.assertIn(t3, r)
        self.assertIn(t4, r)
        self.assertNotIn(t5, r)
        self.assertNotIn(t6, r)

        s, r = List.run(['due+15d'])
        self.assertIn(t1, r)
        self.assertIn(t2, r)
        self.assertIn(t3, r)
        self.assertNotIn(t4, r)
        self.assertNotIn(t5, r)
        self.assertNotIn(t6, r)

        s, r = List.run(['due+0d'])
        self.assertIn(t1, r)
        self.assertIn(t3, r)
        self.assertNotIn(t2, r)
        self.assertNotIn(t4, r)
        self.assertNotIn(t5, r)
        self.assertNotIn(t6, r)

        s, r = List.run(['due+3m'])
        self.assertIn(t1, r)
        self.assertIn(t2, r)
        self.assertIn(t3, r)
        self.assertIn(t4, r)
        self.assertNotIn(t5, r)
        self.assertNotIn(t6, r)

    @skip
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

        s, r = List.run(['remind'])
        self.assertIn(t1, r)
        self.assertIn(t2, r)
        self.assertIn(t3, r)
        self.assertIn(t4, r)
        self.assertNotIn(t5, r)
        self.assertNotIn(t6, r)

        s, r = List.run(['remind+15d'])
        self.assertIn(t1, r)
        self.assertIn(t2, r)
        self.assertIn(t3, r)
        self.assertNotIn(t4, r)
        self.assertNotIn(t5, r)
        self.assertNotIn(t6, r)

        s, r = List.run(['remind+0d'])
        self.assertIn(t1, r)
        self.assertIn(t3, r)
        self.assertNotIn(t2, r)
        self.assertNotIn(t4, r)
        self.assertNotIn(t5, r)
        self.assertNotIn(t6, r)

        s, r = List.run(['remind+3m'])
        self.assertIn(t1, r)
        self.assertIn(t2, r)
        self.assertIn(t3, r)
        self.assertIn(t4, r)
        self.assertNotIn(t5, r)
        self.assertNotIn(t6, r)

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

        s, r = List.run({'parent': {'folder': '', 'keywords': ['project']}})
        self.assertNotIn(t2, r)
        self.assertIn(t1, r)
        self.assertIn(t3, r)

        s, r = List.run({'parent': {'folder': 'next', 'keywords': ['project']}})
        self.assertNotIn(t2, r)
        self.assertIn(t1, r)
        self.assertIn(t3, r)

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
        List.run({'keywords': ['grok']})
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
        s, r = List.run({})
        self.assertIn(t1, r)
        self.assertIn(t2, r)
        self.assertNotIn(t3, r)

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
        s, r = List.run({'parent': {'folder': '', 'keywords': ['project']}})
        self.assertNotIn(t2, r)
        self.assertIn(t1, r)
        self.assertIn(t3, r)

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

        s, r = List.run({'folder': 'today'})
        self.assertEqual(t3, r[0])
        self.assertEqual(t2, r[1])
        self.assertEqual(t1, r[2])


@patch('todone.backend.commands.List.is_loading_saved_search')
class UnitTestListItems(TestCase):
    def setUp(self):
        self.args = {
            'file': 'test',
            'folder': None,
            'parent': None,
        }

    @patch('todone.backend.commands.backend.SavedList')
    def test_if_loading_saved_search_then_calls_loader(
        self, MockSavedList, mock_is_loading
    ):
        mock_is_loading.return_value = True
        List.run(self.args)
        MockSavedList.get_todos_in_list.assert_called_once_with(
            self.args['file'])

    @patch('todone.backend.commands.backend.SavedList')
    def test_if_loading_saved_search_then_does_not_saves_query(
        self, MockSavedList, mock_is_loading
    ):
        mock_is_loading.return_value = True
        List.run(self.args)
        MockSavedList.save_search.assert_not_called()

    @patch('todone.backend.commands.backend.SavedList')
    def test_if_loading_saved_search_then_saves_as_most_recent_query(
        self, MockSavedList, mock_is_loading
    ):
        mock_is_loading.return_value = True
        MockSavedList.get_todos_in_list.return_value = 'test'
        List.run(self.args)
        MockSavedList.save_most_recent_search.assert_called_once_with('test')

    @patch('todone.backend.commands.backend.Todo.query')
    @patch('todone.backend.commands.backend.SavedList')
    def test_if_not_loading_saved_search_then_constructs_query(
        self, MockSavedList, mock_construct, mock_is_loading
    ):
        mock_is_loading.return_value = False
        List.run(self.args)
        mock_construct.assert_called_once_with(**self.args)

    @patch('todone.backend.commands.backend.Todo.query')
    @patch('todone.backend.commands.backend.SavedList')
    def test_if_not_loading_saved_search_then_saves_query(
        self, MockSavedList, mock_construct, mock_is_loading
    ):
        mock_is_loading.return_value = False
        mock_construct.return_value = 'test todo'
        List.run(self.args)
        MockSavedList.save_search.assert_called_once_with(
            self.args['file'], 'test todo')

    @patch('todone.backend.commands.backend.Todo.query')
    @patch('todone.backend.commands.backend.SavedList')
    def test_if_not_loading_saved_search_then_saves_as_most_recent_query(
        self, MockSavedList, mock_construct, mock_is_loading
    ):
        mock_is_loading.return_value = False
        mock_construct.return_value = 'test todo'
        List.run(self.args)
        MockSavedList.save_most_recent_search.assert_called_once_with(
            'test todo')


class TestIsLoading(TestCase):
    def test_empty_dict_arg_returns_True(self):
        self.assertTrue(List.is_loading_saved_search({}))

    def test_dict_with_all_false_values_return_True(self):
        test = {
            'key1': None,
            'key2': [],
            'key3': ''
        }
        self.assertTrue(List.is_loading_saved_search(test))

    def test_dict_with_a_true_value_returns_False(self):
        test = {
            'key1': None,
            'key2': True,
            'key3': ''
        }
        self.assertFalse(List.is_loading_saved_search(test))

    def test_dict_with_only_non_false_being_file_returns_True(self):
        test = {
            'file': 'test',
            'key1': None,
            'key2': [],
            'key3': ''
        }
        self.assertTrue(List.is_loading_saved_search(test))

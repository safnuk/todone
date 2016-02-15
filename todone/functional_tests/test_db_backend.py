from contextlib import redirect_stdout
import io

from django.test import TestCase

from ..actions import SCRIPT_DESCRIPTION
from ..__main__ import main
from ..todos import folders
from todos.db.models import Todo

class DB_Backend(TestCase):

    def test_help_arg_returns_help_string(self):
        f = io.StringIO()
        with redirect_stdout(f):
            main(['help'])
        s = f.getvalue()
        self.assertIn(SCRIPT_DESCRIPTION, s)

    def test_default_list_is_today_items(self):
        t1 = Todo(action='Item 1', folder=folders.INBOX)
        t1.save()
        t2 = Todo(action='Item 2', folder=folders.NEXT)
        t2.save()
        t3 = Todo(action='Item 3', folder=folders.TODAY)
        t3.save()
        f = io.StringIO()
        with redirect_stdout(f):
            main(args=['list'])
        s = f.getvalue()
        self.assertNotIn('Item 1', s)
        self.assertNotIn('Item 2', s)
        self.assertIn('___ Item 3', s)



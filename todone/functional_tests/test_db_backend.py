from contextlib import redirect_stdout
import io

from django.test import TestCase

from ..__main__ import main

class DB_Backend(TestCase):
    def test_empty_arguments_returns_help_string(self):
        f = io.StringIO()
        with redirect_stdout(f):
            main(args=[])
        s = f.getvalue()
        self.assertIn('Welcome to todone', s)


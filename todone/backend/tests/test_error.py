from unittest import TestCase

from todone.backend.commands import Error


class TestErrorAction(TestCase):
    def test_error_is_reflected_back_unchanged(self):
        msg = {'message': 'This is an error!'}
        status, response = Error.run(msg)
        self.assertEqual(status, 'error')
        self.assertEqual(response, msg['message'])

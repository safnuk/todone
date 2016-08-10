from datetime import date
from dateutil.relativedelta import relativedelta
from unittest import TestCase

from todone.parser.format import (
    ApplyFunctionFormat,
    DateFormat,
    PassthroughFormat,
)


class TestPassthroughFormat(TestCase):
    def test_values_are_left_untouched(self):
        formatter = PassthroughFormat()
        value = ['a', 'b', 'C']
        output = formatter.format(value)
        self.assertEqual(value, output)

    def test_empty_list_returns_empty_list(self):
        formatter = PassthroughFormat()
        output = formatter.format([])
        self.assertEqual(output, [])


class TestApplyFunctionFormat(TestCase):
    def test_format_function_is_applied_to_value(self):
        class MockFormatFunction():
            def __init__(self):
                self.call_list = []

            def mock_format(self, value):
                self.call_list.append(value)
                return value
        mock_ff = MockFormatFunction()
        formatter = ApplyFunctionFormat(format_function=mock_ff.mock_format)
        value = ['arg1', 'arg2']
        formatter.format(value)
        self.assertEqual(mock_ff.call_list, [value, ])


class TestDateFormat(TestCase):

    def test_no_date_offset_returns_max_date(self):
        max_date = date(9999, 12, 31)
        formatter = DateFormat()
        match = MockDateMatch()
        output = formatter.format([match, ])
        self.assertEqual(output, max_date)

    def test_day_offset_shifts_date_by_correct_amount(self):
        offset = date.today()
        offset += relativedelta(days=5)
        formatter = DateFormat()
        match = MockDateMatch(5, 'd')
        output = formatter.format([match, ])
        self.assertEqual(output, offset)

    def test_week_offset_shifts_date_by_correct_amount(self):
        offset = date.today()
        offset += relativedelta(weeks=5)
        formatter = DateFormat()
        match = MockDateMatch(5, 'w')
        output = formatter.format([match, ])
        self.assertEqual(output, offset)

    def test_month_offset_shifts_date_by_correct_amount(self):
        offset = date.today()
        offset += relativedelta(months=5)
        formatter = DateFormat()
        match = MockDateMatch(5, 'm')
        output = formatter.format([match, ])
        self.assertEqual(output, offset)

    def test_year_offset_shifts_date_by_correct_amount(self):
        offset = date.today()
        offset += relativedelta(years=5)
        formatter = DateFormat()
        match = MockDateMatch(5, 'y')
        output = formatter.format([match, ])
        self.assertEqual(output, offset)


class MockDateMatch():
    def __init__(self, offset=None, interval=None):
        self.offset = offset
        self.interval = interval

    def groups(self):
        if self.offset and self.interval:
            return (
                'due', '+',
                '{}'.format(self.offset),
                '{}'.format(self.interval)
            )
        else:
            return ('due', )

    def group(self, index):
        if index == 0:
            if self.offset and self.interval:
                return 'due+{}{}'.format(self.offset, self.interval)
            else:
                return 'due'
        if index == 1 or index == 'name':
            return 'due'
        if not (self.offset and self.interval):
            raise IndexError
        if index == 2 or index == 'sign':
            return '+'
        if index == 3 or index == 'offset':
            return '{}'.format(self.offset)
        if index == 4 or index == 'interval':
            return '{}'.format(self.interval)
        raise IndexError

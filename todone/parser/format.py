import datetime
import dateutil.relativedelta


class AbstractFormat(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, value):
        raise NotImplementedError("Subclass must implement virtual method")


class ApplyFunctionFormat(AbstractFormat):
    def __init__(self, format_function=None, *args, **kwargs):
        self.format_function = format_function
        super().__init__(*args, **kwargs)

    def format(self, value):
        if self.format_function:
            return self.format_function(value)
        return value


class PassthroughFormat(ApplyFunctionFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DateFormat(AbstractFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, values):
        if not values:
            return None
        value = values[0]
        offset_date = datetime.date.today()
        if len(value.groups()) == 1:
            return datetime.date(9999, 12, 31)
        offset = int(value.group('offset'))
        interval = value.group('interval').lower()
        if 'days'.startswith(interval):
            offset_date += dateutil.relativedelta.relativedelta(days=offset)
        elif 'weeks'.startswith(interval):
            offset_date += dateutil.relativedelta.relativedelta(weeks=offset)
        elif 'months'.startswith(interval):
            offset_date += dateutil.relativedelta.relativedelta(months=offset)
        elif 'years'.startswith(interval):
            offset_date += dateutil.relativedelta.relativedelta(years=offset)
        return offset_date

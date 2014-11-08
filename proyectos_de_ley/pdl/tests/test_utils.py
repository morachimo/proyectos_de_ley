import datetime

from django.test import TestCase

from pdl.utils import convert_string_to_time, convert_date_to_string


class TestUtils(TestCase):
    def test_convert_string_to_time(self):
        string = "2014-10-10"
        expected = datetime.datetime(2014, 10, 10)
        result = convert_string_to_time(string)
        self.assertEqual(expected, result)

        string = "2014-10-10 10:20:10.23"
        expected = datetime.datetime(2014, 10, 10, 10, 20, 10, 230000)
        result = convert_string_to_time(string)
        self.assertEqual(expected, result)

        string = "2014-10-10 10:20:10"
        expected = datetime.datetime(2014, 10, 10, 10, 20, 10)
        result = convert_string_to_time(string)
        self.assertEqual(expected, result)

    def test_convert_date(self):
        date = datetime.date(2014, 10, 28)
        result = convert_date_to_string(date)
        expected = '10/28/2014'
        self.assertEqual(expected, result)

        date = "2014-10-28"
        result = convert_date_to_string(date)
        self.assertIsNone(result)

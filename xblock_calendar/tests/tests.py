from unittest import TestCase
from collections import namedtuple
from mock import patch
import datetime
from xblock.runtime import Runtime
import xblock_calendar.xblock_calendar as calendar


class MiddlemanTestCase(TestCase):

    @classmethod
    def setUpClass(self):
        self.test_data = eval(open('xblock_calendar/tests/test_data.txt', 'r').read())
        self.middleman = calendar.Middleman(self.test_data, 0)
        self.Event = namedtuple('event', 'start summary')
        self.today = datetime.datetime(2013, 7, 31, 0, 0)

    def mock_today():
        return datetime.datetime(2013, 7, 31, 0, 0)

    def next_week():
        return datetime.datetime(2013, 7, 31, 0, 0) + datetime.timedelta(days=7)

    def next_month():
        return datetime.datetime(2013, 7, 31, 0, 0) + datetime.timedelta(days=28)

    def past_expiry():
        return datetime.datetime(2013, 7, 31, 0, 0) + datetime.timedelta(days=70)

    @patch('xblock_calendar.xblock_calendar.today', mock_today)
    def test_context_today(self):
        self.middleman = calendar.Middleman(self.test_data, 0)
        defendant = self.middleman._context()
        expected = {'Events': {'Fri': [u'CS-191 pset due'],
                               'Mon': [],
                               'Sat': [u'Sabbath'],
                               'Sun': [u'dance lessons'],
                               'Thu': [],
                               'Tue': [],
                               'Wed': [u'HLS1x Exam 2',
                                       u'BPMG Project Night']},
                    'Dates': {'Mon': 'Mon.29',
                              'Tue': 'Tue.30',
                              'Wed': 'Wednesday.31',
                              'Thu': 'Thu.1',
                              'Fri': 'Fri.2',
                              'Sat': 'Sat.3',
                              'Sun': 'Sun.4'},
                    'Order': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'Today': 'July 31, 2013'
                    }
        for weekday in defendant['Events']:
            self.assertEqual(sorted(defendant['Events'][weekday]), sorted(expected['Events'][weekday]),
                             'For {2}, got {0} but expected {1}'.format(sorted(defendant['Events'][weekday]), sorted(expected['Events'][weekday]), weekday))
        for weekday in defendant['Dates']:
            self.assertEqual(defendant['Dates'][weekday], expected['Dates'][weekday])

    @patch('xblock_calendar.xblock_calendar.today', next_week)
    def test_context_next_week(self):
        defendant = self.middleman._context()
        expected = {'Events': {'Fri': [u'CS-191 pset due'],
                               'Mon': [],
                               'Sat': [u'Sabbath'],
                               'Sun': [u'dance lessons'],
                               'Thu': [],
                               'Tue': [],
                               'Wed': []},
                    'Dates': {'Mon': 'Mon.5',
                              'Tue': 'Tue.6',
                              'Wed': 'Wednesday.7',
                              'Thu': 'Thu.8',
                              'Fri': 'Fri.9',
                              'Sat': 'Sat.10',
                              'Sun': 'Sun.11'},
                    'Order': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'Today': 'August 07, 2013'
                    }
        for weekday in defendant['Events']:
            self.assertEqual(sorted(defendant['Events'][weekday]), sorted(expected['Events'][weekday]),
                             defendant['Events'])
        for weekday in defendant['Dates']:
            self.assertEqual(defendant['Dates'][weekday], expected['Dates'][weekday])

    @patch('xblock_calendar.xblock_calendar.today', next_month)
    def test_context_next_month(self):
        self.middleman = calendar.Middleman(self.test_data, 0)
        defendant = self.middleman._context()
        expected = {'Events': {'Fri': [u'CS-191 pset due'],
                               'Mon': [],
                               'Sat': [u'Sabbath'],
                               'Sun': [u'dance lessons'],
                               'Thu': [],
                               'Tue': [],
                               'Wed': [u'BPMG Project Night']},
                    'Dates': {'Mon': 'Mon.26',
                              'Tue': 'Tue.27',
                              'Wed': 'Wednesday.28',
                              'Thu': 'Thu.29',
                              'Fri': 'Fri.30',
                              'Sat': 'Sat.31',
                              'Sun': 'Sun.1'},
                    'Order': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'Today': 'August 28, 2013'
                    }
        for weekday in defendant['Events']:
            self.assertEqual(sorted(defendant['Events'][weekday]), sorted(expected['Events'][weekday]),
                             'For {2} got {0} but expected {1}'.format(sorted(defendant['Events'][weekday]), sorted(expected['Events'][weekday]), weekday))
        for weekday in defendant['Dates']:
            self.assertEqual(defendant['Dates'][weekday], expected['Dates'][weekday])

    @patch('xblock_calendar.xblock_calendar.today', past_expiry)
    def test_events_expire(self):
        self.middleman = calendar.Middleman(self.test_data, 0)
        defendant = self.middleman._context()
        expected = {'Events': {'Fri': [],
                               'Mon': [],
                               'Sat': [u'Sabbath'],
                               'Sun': [],
                               'Thu': [],
                               'Tue': [],
                               'Wed': []},
                    'Dates': {'Mon': 'Mon.7',
                              'Tue': 'Tue.8',
                              'Wed': 'Wednesday.9',
                              'Thu': 'Thu.10',
                              'Fri': 'Fri.11',
                              'Sat': 'Sat.12',
                              'Sun': 'Sun.13'},
                    'Order': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'Today': 'August 10, 2013'
                    }
        for weekday in defendant['Events']:
            self.assertEqual(sorted(defendant['Events'][weekday]), sorted(expected['Events'][weekday]),
                             'For {2} got {0} but expected {1}'.format(sorted(defendant['Events'][weekday]), sorted(expected['Events'][weekday]), weekday))
        for weekday in defendant['Dates']:
            self.assertEqual(defendant['Dates'][weekday], expected['Dates'][weekday])

import requests
import datetime
import json
import calendar
import pkg_resources
from jinja2 import Environment, PackageLoader
from collections import namedtuple

from xblock.core import XBlock
from xblock.fields import Scope, String, Dict, Integer, Any
from xblock.fragment import Fragment


def today():
    """
    Returns the current local date.
    Here for the purpose of easily manipulating
    what the tests think is the current local date.
    """
    return datetime.datetime.now()


class EventHandler(object):
    """
    This class contains the necessary methods to parse the response from the
    Google Calendar API and make it accessible to the client side.
    """
    def __init__(self, events, offset):
        self.data = events
        self.offset = offset
        self.formatted_events = []

    @staticmethod
    def format_event(event):
        """
        `event` is a dictionary returned by the Calendar API. It contains
        all information for an event in the calendar.
        Returns a triple with the start date, summary, and recurrence information.
        """
        try:
            year, month, day = unicode.encode(event['start']['date'])[:10].split('-')
        except:
            year, month, day = unicode.encode(event['start']['dateTime'])[:10].split('-')
        if 'recurrence' in event:
            return (datetime.datetime(int(year), int(month), int(day)), event['summary'], event['recurrence'])
        else:
            return (datetime.datetime(int(year), int(month), int(day)), event['summary'], None)

    @staticmethod
    def parse_recurrence(recurrence):
        """
        Recurrence is a list with one element containing
        the recurrence information of a calendar event.
        It looks something like this:
        [u'RRULE:FREQ=WEEKLY;UNTIL=20130901T160000Z;BYDAY=SU']
        """
        toReturn = {}
        info = recurrence[0].split(':')[1].split(';')
        for field in info:
            key, value = field.split('=')
            toReturn[key] = value
        return toReturn

    @staticmethod
    def parse_date(datestring):
        """
        `datestring` is a string of the form "20130901T160000Z".
        Returns a datetime object encoding the information in `datestring`.
        """
        date = datestring.split('T')[0]
        return datetime.datetime(int(date[:-4]), int(date[-4:-2]), int(date[-2:]))

    @staticmethod
    def monday_of(date):
        """
        `date` is a datetime object.
        Returns the datetime object corresponding to the Monday before `date`.
        """
        return date - datetime.timedelta(days=date.weekday(), hours=date.hour, minutes=date.minute,
                                         seconds=date.second, microseconds=date.microsecond)

    @staticmethod
    def week_count(now, event_start, recurrence):
        if (now-event_start).days/7 >= int(recurrence['COUNT']):
            return False
        else:
            return True

    @staticmethod
    def month_count(now, event_start, recurrence):
        if (now - event_start).days/28 >= int(recurrence['COUNT']):
            return False
        else:
            return True

    def is_this_week(self, formatted_event):
        """
        `formatted_event` is an ordered triple whose elements encode a calendar event's
        starting date, summary, and recurrence information respectively.
        Returns True iff `formatted_event` happens within the current week.
        A week starts on Monday and ends on Sunday.
        """
        # week_start is 12AM of the most recent Monday
        Event = namedtuple('event', 'start summary')
        now = today() + datetime.timedelta(days=7*self.offset)
        monday = self.monday_of(now)
        event_start = formatted_event[0]
        recurrence = formatted_event[2]

        # maps recurrence types to the functions that process them
        count_dictionary = {'MONTHLY': self.month_count, 'WEEKLY': self.week_count}

        # True for non-recurring events happening this week
        if recurrence is None and self.monday_of(event_start) == monday:
            if self.monday_of(event_start) == monday:
                return True
            else:
                return False

        # start logic to return True for recurring events whose initial
        # start date is this week or earlier
        elif recurrence is not None and not self.monday_of(event_start) > monday:
            recurrence = self.parse_recurrence(recurrence)

            # handles events that should stop appearing in calendar
            # after a certain date
            if 'UNTIL' in recurrence and monday > self.monday_of(self.parse_date(recurrence['UNTIL'])):
                return False

            # handles events that are only supposed to happen a
            # certain number of times
            if 'COUNT' in recurrence:
                return count_dictionary[recurrence['FREQ']](now, event_start, recurrence)

            # adds a copy of the event for each day of the week
            # and returns false to avoid getting a repeated event
            elif recurrence['FREQ'] == 'DAILY':
                event_monday = self.monday_of(event_start)
                for i in range(7):
                    event = Event(event_monday + datetime.timedelta(days=i), formatted_event[1])
                    self.formatted_events.append(event)
                return False

            # adds a copy of the event for each day of the week
            # on which it happens and then returns false to avoid repeats
            elif recurrence['FREQ'] == 'WEEKLY':
                if 'BYDAY' in recurrence:
                    all_days = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
                    relevant_days = recurrence['BYDAY'].split(',')
                    event_monday = self.monday_of(event_start)
                    for i in range(7):
                        if all_days[i] in relevant_days:
                            event = Event(monday + datetime.timedelta(days=i), formatted_event[1])
                            self.formatted_events.append(event)
                    return False
                else:
                    return True

            # returns True if the number of weeks since the event happened is
            # a multiple of four.
            elif recurrence['FREQ'] == 'MONTHLY':
                if (monday - self.monday_of(event_start)).days % 28 == 0:
                    return True
                else:
                    return False

    def format_events(self):
        """
        Applies map and filter to the data received by the Google Calendar API and
        returns only the events ocurring on what the calendar thinks is the current week,
        based on `self.offset`.
        """
        Event = namedtuple('event', 'start summary')
        raw_events = self.data['items']
        cooked_events = map(self.format_event, raw_events)
        # relevant_events represents this week's events
        relevant_events = filter(self.is_this_week, cooked_events)
        for event in relevant_events:
            start, summary, recurrence = event
            self.formatted_events.append(Event(start, summary))

        return self.formatted_events

TEMPLATE_LOADER = PackageLoader(__package__, 'static')
TEMPLATE_ENV = Environment(loader=TEMPLATE_LOADER,
                           lstrip_blocks=True,
                           trim_blocks=True)


class Middleman(object):
    """
    Handles communication between python code and the html template.
    """
    TEMPLATE_NAME = 'html/calendar_template.html'

    def __init__(self, response, offset):
        self.data = response
        self.offset = offset

    def render_template(self):
        """
        Populates the calendar template with the data obtained from the calendar.
        """
        html_file_path = pkg_resources.resource_filename(__name__, "static/html/student_view.html")
        html_file = open(html_file_path, 'w')

        if self.TEMPLATE_NAME is not None:
            # Find the template
            template = TEMPLATE_ENV.get_template(self.TEMPLATE_NAME)
            # Render the template
            report = template.render(self._context())
            # Write the events to the html file that will be displayed.
            # (encode to a byte string)
            html_file.write(report.encode('utf-8'))

    def _context(self):
        """
        Returns a dictionary containing the information we want the template to read and display.
        """
        formatted_events = EventHandler(self.data, self.offset).format_events()
        events = {'Events': {'Mon': [],
                  'Tue': [],
                  'Wed': [],
                  'Thu': [],
                  'Fri': [],
                  'Sat': [],
                  'Sun': []},
                  'Dates': {}}
        weekdays = [day[0:3] for day in list(calendar.day_name)]
        for event in formatted_events:
            events['Events'][weekdays[event.start.weekday()]].append(event.summary)
        now = today() + datetime.timedelta(days=7*self.offset)
        monday = EventHandler.monday_of(now)
        for i in range(7):
            events['Dates'][weekdays[i]] = '{0}.{1}'.format(weekdays[i], (monday + datetime.timedelta(days=i)).day)
        events['Dates'][weekdays[now.weekday()]] = '{0}.{1}'.format(list(calendar.day_name)[now.weekday()],
                                                                    now.day)
        events['Order'] = weekdays
        events['Today'] = '{0} {1}, {2}'.format(list(calendar.month_name)[now.month], now.day, now.year)
        return events


class CalendarBlock(XBlock):
    """
    An XBlock that allows that requests access to a Google calendar using OAuth2
    and then displays the contents to the students.
    """

    email = String(help="Email address of the google-compatible account whose calendar we wish to display",
                   default='xblockcalendar@dmail.com',
                   scope=Scope.settings)
    credentials = Dict(help="Stores access token required for calls to the Google Calendar API",
                       default=None,
                       scope=Scope.settings)
    offset = Integer(help="Number of weeks into the future for which we are displaying calendar events.",
                     default=0,
                     scope=Scope.settings)
    api_response = Any(help="Response from the call the Google Calendar API",
                       scope=Scope.settings)

    def instructor_view(self, context):
        """
        Create a fragment used to display the XBlock to a student.
        `context` is a dictionary used to configure the display (unused).
        Returns a `Fragment` object specifying the HTML, CSS, and JavaScript
        """
        self.render_template()
        html_str = pkg_resources.resource_string(__name__, "static/html/student_view.html")
        frag = Fragment(unicode(html_str))
        css_str = pkg_resources.resource_string(__name__, "static/css/student_view.css")
        frag.add_css(unicode(css_str))
        js_str = pkg_resources.resource_string(__name__, "static/js/student_view.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('CalendarBlock')
        return frag

    def student_view(self, context):
        """
        `context` is a dictionary used to configure the display (unused).
        `response` is a string containing the result of trying to obtaine an
        authorization code to create an access token for the Google Calendar API.
        Creates a fragment used to display the XBlock to an instructor. If response
        is not None `grant_access` is called.
        Returns a `Fragment` object specifying the HTML, CSS, and JavaScript
        """
        html_str = pkg_resources.resource_string(__name__, "static/html/instructor_view.html")
        frag = Fragment(unicode(html_str))
        css_str = pkg_resources.resource_string(__name__, "static/css/instructor_view.css")
        frag.add_css(unicode(css_str))
        js_str = pkg_resources.resource_string(__name__, "static/js/instructor_view.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('CalendarBlock')
        return frag

    @XBlock.json_handler
    def endpoint(self, response):
        """
        Endpoint for communication between the server and the client.
        """
        if 'email' in response:
            self.email = response['email']
        elif 'travel' in response:
            if response['travel'] == 'forward':
                self.offset += 1
                middleman = Middleman(self.api_response, self.offset)
                return middleman._context()
            elif response['travel'] == 'backward':
                self.offset -= 1
                middleman = Middleman(self.api_response, self.offset)
                return middleman._context()
            else:
                self.offset = 0
                middleman = Middleman(self.api_response, self.offset)
                return middleman._context()

    @XBlock.query_handler
    def grant_access(self, response):
        """
        `response` is a string containing the result of trying to obtaine an
        authorization code to create an access token for the Google Calendar API.
        If `response` contains an authorization code, `grant_access` uses that code
        to obtain an access token and a refresh token from Google.
        """
        parameters = {'code': response['code'],
                      'client_id': '596157636159-svpcup864oijtk6s4jd538sqs9156d6i.apps.googleusercontent.com',
                      'client_secret': 'vIPi7QA4aJmLWrv1c7t2KCda',
                      'redirect_uri': 'http://localhost:8002{0}'.format(self.runtime.handler_url(self, 'grant_access')),
                      'grant_type': 'authorization_code',
                      }
        response = requests.post('https://accounts.google.com/o/oauth2/token', params=parameters, data=parameters)
        self.credentials = json.loads(response.text)

    def render_template(self):
        parameters = {'access_token': self.credentials['access_token'],
                      'refresh_token': self.credentials['refresh_token']}
        self.api_response = json.loads((requests.get('https://www.googleapis.com/calendar/v3/calendars/{0}/events'.format(self.email),
                                        params=parameters)).content)
        middleman = Middleman(self.api_response, self.offset)
        middleman.render_template()

    @staticmethod
    def workbench_scenarios():
        """
        A canned scenario for display in the workbench.
        """
        return [
            ("Calendar",
                """\
                        <Calendar />
                """)
        ]

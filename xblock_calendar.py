import httplib2
import datetime
import pkg_resources
from jinja2 import Environment, PackageLoader
from collections import namedtuple
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

from xblock.core import XBlock, Scope, String
from xblock.fragment import Fragment


class Authentication(object):
    """
    Handles the creation of access tokens for the Google Calendar API.
    """
    def __init__(self):

        FLOW = OAuth2WebServerFlow(
            client_id='183834599317.apps.googleusercontent.com',
            client_secret='F9ek5BElDqYCsyZSQNgQBMVU',
            scope='https://www.googleapis.com/auth/calendar.readonly',
            user_agent='xblock-calendar/0.2',
            access_type='offline')

        storage = Storage('calendar.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid == True:
            credentials = run(FLOW, storage)

        http = httplib2.Http()
        http = credentials.authorize(http)

        service = build(serviceName='calendar',
                        version='v3',
                        http=http)

        self.service = service


class Formatter(object):
    """
    Converts the json obtained through the Google Calendar API into
    """
    def __init__(self, authenticator, email):
        self.service = authenticator.service
        self.email = email

    def format_events(self):
        """
        """
        formatted_events = []
        Event = namedtuple('event', 'start summary')

        data = self.service.events().list(calendarId=self.email).execute()
        raw_events = data['items']

        for i in range(len(raw_events)):
            year, month, day = unicode.encode(raw_events[i]['start']['dateTime'])[:10].split('-')
            formatted_events.append(Event(datetime.date(int(year), int(month), int(day)),
                                          raw_events[i]['summary']))
        return formatted_events


TEMPLATE_LOADER = PackageLoader(__file__, 'static')
TEMPLATE_ENV = Environment(loader=TEMPLATE_LOADER,
                           lstrip_blocks=True,
                           trim_blocks=True)


class Middleman(object):
    """
    Handles communication between the code and the template.
    """
    TEMPLATE_NAME = 'html/calendar_template.html'

    def __init__(self, email):
        self.email = email

    def generate_html(self):
        """
        Populates the calendar template with the data obtained from the calendar corresponding to `self.email`.
        """
        html_file_path = '../.virtualenvs/edx-platform/src/xblock-calendar/static/html/calendar02.html'
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
        auth = Authentication()
        formatted_events = Formatter(auth, self.email).format_events()
        events = {'Weekdays': {'Monday': [],
                  'Tuesday': [],
                  'Wednesday': [],
                  'Thursday': [],
                  'Friday': [],
                  'Saturday': [],
                  'Sunday': []},
                  'Dates': {}}
        for event in formatted_events:
            events['Weekdays'][events['Weekdays'].keys()[event.start.weekday()]].append(event)

        return events


class CalendarBlock(XBlock):
    """
    An XBlock that pulls information from an existing Google Calendar and displays it in the workbench.
    """

    email = String(help="Email address of the google-compatible account whose calendar we wish to display",
                   default=None,
                   scope=Scope.settings)

    def student_view(self, context):
        """
        Create a fragment used to display the XBlock to a student.
        `context` is a dictionary used to configure the display (unused)

        Returns a `Fragment` object specifying the HTML, CSS, and JavaScript
        """

        middleman = Middleman(self.email)
        middleman.generate_html()
        html_str = pkg_resources.resource_string(__name__, "static/html/calendar02.html")

        return Fragment(unicode(html_str))

    @staticmethod
    def workbench_scenarios():
        """
        A canned scenario for display in the workbench.
        """
        return [
            ("Calendar",
                """\
                    <vertical>
                        <Calendar email="xblockcalendar@gmail.com" />
                        <Thumbs />
                    </vertical>
                """)
        ]

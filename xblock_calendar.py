import httplib2
import datetime
import os
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
    """
    def __init__(self):

        FLOW = OAuth2WebServerFlow(
            client_id='596157636159.apps.googleusercontent.com',
            client_secret='mQSWQ6eC1kl9kxmbojqMwl8M',
            scope='https://www.googleapis.com/auth/calendar.readonly',
            user_agent='xblock-calendar/0.2')

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
    """
    def __init__(self, authenticator):
        self.service = authenticator.service

    def format_events(self):
        """
        """
        formatted_events = []
        Event = namedtuple('event', 'start summary')

        data = self.service.events().list(calendarId='xblockcalendar@gmail.com').execute()
        raw_events = data['items']

        for i in range(len(raw_events)):
            year, month, day = unicode.encode(raw_events[i]['start']['dateTime'])[:10].split('-')
            formatted_events.append(Event(datetime.date(int(year), int(month), int(day)),
                                          raw_events[i]['summary']))
        return formatted_events

TEMPLATE_LOADER = PackageLoader('xblock_calendar', 'static')
TEMPLATE_ENV = Environment(loader=TEMPLATE_LOADER,
                           lstrip_blocks=True,
                           trim_blocks=True)

class TemplateGenerator(object):
    """
    Reporter that uses a template to generate the report.
    """
    TEMPLATE_NAME = 'html/calendar_template.html'

    def generate_report(self):
        """
        See base class.
        """
        html_file_path = 'xblock-calendar/static/html/calendar02.html'
        html_file = open(html_file_path, 'w')

        if self.TEMPLATE_NAME is not None:

            # Find the template
            template = TEMPLATE_ENV.get_template(self.TEMPLATE_NAME)

            # Render the template
            report = template.render(self._context())

            # Write the report to the output file
            # (encode to a byte string)
            html_file.write(report.encode('utf-8'))

    def _context(self):
        """

        """
        auth = Authentication()
        formatted = Formatter(auth).format_events()
        events = {'Days': {'Monday': [],
                  'Tuesday': [],
                  'Wednesday': [],
                  'Thursday': [],
                  'Friday': [],
                  'Saturday': [],
                  'Sunday': []}}
        for event in formatted:
            events['Days'][events['Days'].keys()[event.start.weekday()]].append(event)
        return events


class CalendarBlock(XBlock):
    """
    Calendar
    """

    email = String(help="Email address of the google-compatible account whose calendar we wish to display",
                   default=None,
                   scope=Scope.settings)

    def student_view(self, context):

	blarg = TemplateGenerator()
	blarg.generate_report()
        html_str = pkg_resources.resource_string(__name__, "templates/calendar02.html")

        return Fragment(unicode(html_str))

    #@staticmethod
    #def workbench_scenario():
    #    """
    #    A canned scenario for display in the workbench.
    #    """
    #    return [
    #        ("Calendar",
    #        """\
    #            <vertical>
    #                <Calendar/>
    #            </vertical>
    #        """)
    #    ]


from xblock.core import XBlock, Scope, String
from xblock.fragment import Fragment
import pkg_resources

class CalendarBlock(XBlock):
    """
    Calendar
    """

    email = String(help="Email address of the google-compatible account whose calenar we wish the display",
                   default=None,
                   scope=Scope.settings)

    def student_view(self, context):


        embed_code = '<iframe src="http://www.google.com/calendar/embed?src=jnater%40edx.org&ctz=America/New_York" style="border: 0" width="800" height="600" frameborder="0" scrolling="no"></iframe>'
        html_str = pkg_resources.resource_string(__name__, "static/html/calendar.html")

        return Fragment(unicode(html_str).format(self=self, embed_code=embed_code))

    @staticmethod
    def workbench_scenario():
        """
        A canned scenario for display in the workbench.
        """
        return [
            ("Calendar",
            """\
                <vertical>
                    <calendar/>
                </vertical>
            """)
        ]

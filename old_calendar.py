from xblock.core import XBlock, Scope, String
from xblock.fragment import Fragment
import pkg_resources


class CalendarBlock(XBlock):
    """
    Calendar
    """

    email = String(help="Email address of the google-compatible account whose calendar we wish the display",
                   default=None,
                   scope=Scope.settings)

    def student_view(self, context):

        html_str = pkg_resources.resource_string(__name__, "static/html/calendar02.html")

        return Fragment(unicode(html_str))

#    @staticmethod
#    def workbench_scenario():
#        """
#        A canned scenario for display in the workbench.
#        """
#        return [
#            ("Calendar",
#            """\
#                <vertical>
#                    <easgasgasgasghad />
#                </vertical>
#            """)
#        ]

from setuptools import setup

setup(
    name='xblock-calendar',
    version='0.1',
    description='Calendar XBlock',
    install_requires=['XBlock'],
    entry_points={
        'xblock.v1': [
            'calendar = old_calendar:CalendarBlock',
        ]
    }
)

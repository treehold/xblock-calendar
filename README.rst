Part of `edX code`__.

__ http://code.edx.org/

Calendar XBlock
=============

**Calendar** is a sample `XBlock`_ written as a separate installable module as
an example of how third-party XBlocks can be structured.

.. _XBlock: https://github.com/edx/XBlock

Installation
------------

This code runs on Python 2.7.

1.  Get a local copy of the `XBlock`_ repository and add the following line to
    the requirements.txt file:

        -e git+http://github.com/edx/xblock-calendar#egg=xblockcalendar

    .. _XBlock: https://github.com/edx/XBlock

2.  Follow the installation instructions in the `XBlock`_ repo's README.rst. 
    Calendar should now appear as a scenario in the workbench.

    .. _XBlock: https://github.com/edx/XBlock
    .. _Google API console: https://accounts.google.com/ServiceLogin?service=devconsole&passive=1209600&continue=https://code.google.com/apis/console/&followup=https://code.google.com/apis/console/

License
-------

The code in this repository is licensed under version 3 of the AGPL unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

How to Contribute
-----------------

Contributions are very welcome. The easiest way is to fork this repo, and then
make a pull request from your fork. The first time you make a pull request, you
may be asked to sign a Contributor Agreement.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org

Mailing List and IRC Channel
----------------------------

You can discuss this code on the `edx-xblock Google Group`__ or in the
``edx-code`` IRC channel on Freenode.

__ https://groups.google.com/forum/#!forum/edx-xblock
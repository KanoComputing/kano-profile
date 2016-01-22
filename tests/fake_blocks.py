#!/usr/bin/env python
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#  This is a standalone webapp to simulate Minecraft and Pong.
#  It is launched by the tests to fake the Kano World share signals.
#
#  To close the app, send the literal "window.open('', '_self', ''); window.close();"
#  through the webapp pipe - instance._pipe_name.
#

from kano.webapp import WebApp
import sys

fake_html='/tmp/fake_minecraft.html'

class FakeWebApp(WebApp):
    def __init__(self, app_name):
        super(FakeWebApp, self).__init__()
        self._index=fake_html
        self._title=app_name
        self._width=800
        self._height=600
        self._x = 5
        self._y = 5

fake_html_code='''
<html>
<head>
<script>
var Signal = {};

Signal.load = function(xmlfile) {
  /* a message box with the xml will popup */
  /* the tests can look for it with "xwininfo" */
  alert(xmlfile);
};

</script>
</head>

<h3>Fake WebApp to intercept KanoWorld open share signals</h3>
<body>
</body>
</html>
'''


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print 'Need the name of the fake app (titlebar)'
        sys.exit(0)
    else:
        app_name=sys.argv[1]

    # create our own temporary html front page
    with open(fake_html, 'w') as f:
            f.write(fake_html_code)

    # start minecraft fake window in the background
    fakeapp=FakeWebApp(app_name)
    fakeapp.run()

#!/usr/bin/env python
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#  A simple test to make sure Kano World shares will not open multiple apps.
#
#  You need to run this test on a KanoOS installation, and as a regular user.
#

import unittest
import threading
import os
import time

from kano.webapp import WebApp

fake_html='/tmp/fake_minecraft.html'
fake_xml='/tmp/fake_kano_share.xml'
app_name='make-minecraft'

# TODO: populate to Pong
class FakeMinecraft(WebApp):
    def __init__(self):
        super(FakeMinecraft, self).__init__()
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
var signal_xmlfile = "";

Signal.launch_share = function(xmlfile) {
  signal_xmlfile = xmlfile
};

</script>
</head>

<h3>Fake Minecraft to receive signals from Kano World</h3>
<body>
</body>
</html>
'''

class TestOpenMinecraftShare(unittest.TestCase):

    def setUp(self):
        with open(fake_html, 'w') as f:
            f.write(fake_html_code)
        os.system('touch {}'.format(fake_xml))

    def tearDown(self):
        os.unlink(fake_html)
        os.unlink(fake_xml)
                
    def test_launch_project_api_exists(self):
        from kano_profile.apps import launch_project
        self.assertTrue(launch_project)

    def test_launch_minecraft_project(self):
        '''
        This test will create a fake browser window called Minecraft,
        then request to launch a project, to make sure Minecraft is not started,
        but instead a signal will be sent to our fake instance.
        '''
        from kano_profile.apps import launch_project

        # start minecraft fake window in the background
        fakemc=FakeMinecraft()
        t = threading.Thread(target=fakemc.run)
        t.daemon=True
        t.start()
        time.sleep(3)

        # make sure Minecraft fake window is up
        mcwindow=os.popen('xwininfo -root -tree | grep {}'.format(app_name)).read()
        self.assertIn(app_name, mcwindow)

        # ask MC to open a share, instead of starting a new app instance
        launch_project(app_name, fake_xml, os.path.dirname(fake_xml))
        # TODO: make sure the signal arrived to our javascript
        time.sleep(3)

        # done, close the fake browser now
        f = open (fakemc._pipe_name, 'w')
        f.write("window.open('', '_self', ''); window.close();")
        f.close()

        time.sleep(3)

        # make sure there is no MC instance running
        mcwindow=os.popen('xwininfo -root -tree | grep {}'.format(app_name)).read()
        self.assertFalse(len(mcwindow))

        

if __name__ == '__main__':

    unittest.main()

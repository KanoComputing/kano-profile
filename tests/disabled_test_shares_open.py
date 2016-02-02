#!/usr/bin/env python
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#  A simple test to make sure Kano World shares will not open for Minecraft and Pong.
#
#  You need to run this test on a KanoOS installation, and as a regular user.
#

import unittest
import threading
import os
import time

fake_xml='/tmp/fake_kano_share.xml'

class TestOpenShares(unittest.TestCase):

    def setUp(self):
        '''prepare the fake xml to send to the app'''
        os.system('touch {}'.format(fake_xml))

    def tearDown(self):
        '''cleanup the xml file and kill the fake app'''
        os.unlink(fake_xml)
        self._stop_fake_webapp()

    def _find_x11_app(self, app_name):
        apps=os.popen('xwininfo -root -tree | grep {}'.format(app_name)).read()
        return app_name in apps

    def _start_fake_webapp(self, app_name, delay=8):
        os.system('python fake_blocks.py {} &'.format(app_name))
        time.sleep(delay)
        self.assertTrue(self._find_x11_app(app_name),
                        msg='Could not start fake webapp {}'.format(app_name))

    def _stop_fake_webapp(self, delay=5):
        os.system('pkill -f fake_blocks')
        time.sleep(delay)

    def test_launch_project_api_exists(self):
        from kano_profile.apps import launch_project
        self.assertTrue(launch_project)

    def test_open_minecraft_share(self):
        app_name='make-minecraft'
        from kano_profile.apps import launch_project

        self._start_fake_webapp(app_name)

        # ask Kano Profile to open a share, instead of starting a new app instance
        launch_project(app_name, fake_xml, os.path.dirname(fake_xml), background=True)
        time.sleep(3)

        self._stop_fake_webapp()
        self.assertFalse(self._find_x11_app(app_name), msg='Minecraft unexpectedly running')

    def test_open_pong_share(self):
        app_name='make-pong'
        from kano_profile.apps import launch_project

        self._start_fake_webapp(app_name)

        # ask Kano Profile to open a share, instead of starting a new app instance
        launch_project(app_name, fake_xml, os.path.dirname(fake_xml), background=True)
        time.sleep(3)

        self._stop_fake_webapp()
        self.assertFalse(self._find_x11_app(app_name), msg='Pong unexpectedly running')


if __name__ == '__main__':
    unittest.main()

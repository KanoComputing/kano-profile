
#!/usr/bin/env python

# first_screen.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# First screen of profile on first run
# Launched on straight after kano-settings
# Dependent on internet connection


from gi.repository import Gtk

from kano.gtk3.heading import Heading
from kano.gtk3.green_button import GreenButton
from kano_login import gender, login
from kano.network import is_internet
from kano_profile_gui.images import get_image
import kano.gtk3.cursor as cursor


win = None
box = None
login_button = None
next_button = None
done_button = None


def activate(_win, _box=None):
    global win, box, login_button, done_button, next_button

    img_width = 590
    img_height = 270

    win = _win
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

    img = Gtk.Image()
    box.pack_start(img, False, False, 0)

    if is_internet():
        title = Heading("You've made some progress, let's save it!", "Lets create an account")
        # This button should send you to the login screen
        login_button = GreenButton("I ALREADY HAVE AN ACCOUNT")
        next_button = GreenButton("REGISTER")
        button_box = Gtk.Box()
        button_box.pack_start(login_button.align, False, False, 10)
        button_box.pack_start(next_button.align, False, False, 10)

        button_padding = Gtk.Alignment()
        button_padding.set_padding(0, 20, 80, 0)
        button_padding.add(button_box)

        next_button.connect("button_press_event", update)
        login_button.connect("button_press_event", login_screen)
        box.pack_start(title.container, False, False, 0)
        box.pack_start(button_padding, False, False, 0)

        filename = get_image("login", "", "create-profile", str(img_width) + 'x' + str(img_height))
        img.set_from_file(filename)

    else:
        title = Heading("You should get an account, but you need internet!", "Come back later")
        done_button = GreenButton("DONE")
        done_button.connect("button_press_event", close_window)
        done_button.set_padding(0, 10, 0, 0)
        box.pack_start(title.container, False, False, 0)
        box.pack_start(done_button.align, False, False, 0)
        filename = get_image("login", "", "create-profile_noInternet", str(img_width) + 'x' + str(img_height))
        img.set_from_file(filename)

    win.add(box)
    box.show_all()


def update(widget, event):
    global win, box

    win.remove(box)
    win.pack_grid()
    win.update()
    gender.activate(win, win.box)


def login_screen(widget, event):
    global win, box

    win.remove(box)
    win.pack_grid()
    win.update()
    login.activate(win, win.box)


def close_window(widget, event):
    cursor.arrow_cursor(widget, None)
    Gtk.main_quit()

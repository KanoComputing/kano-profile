
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

from components import heading, green_button
from kano_login import gender, login
from kano.network import is_internet
from kano_profile_gui.images import get_image
import kano_login.components.cursor as cursor


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
    # Placeholder image
    filename = get_image("level", "", "level-1", str(img_width) + 'x' + str(img_height))
    img.set_from_file(filename)
    box.pack_start(img, False, False, 0)

    if is_internet():
        title = heading.Heading("You've made some progress, let's save it!", "Lets create an account")
        # This button should send you to the login screen
        login_button = green_button.Button("I ALREADY HAVE AN ACCOUNT", win)
        next_button = green_button.Button("REGISTER", win)
        button_box = Gtk.Box()
        button_box.pack_start(login_button.align, False, False, 10)
        button_box.pack_start(next_button.align, False, False, 10)

        button_padding = Gtk.Alignment()
        button_padding.set_padding(0, 20, 80, 0)
        button_padding.add(button_box)

        next_button.button.connect("button_press_event", update)
        login_button.button.connect("button_press_event", login_screen)
        box.pack_start(title.container, False, False, 0)
        box.pack_start(button_padding, False, False, 0)

    else:
        title = heading.Heading("You should get an account, but you need internet!", "Come back later")
        done_button = green_button.Button("DONE", win)
        done_button.button.connect("button_press_event", close_window)
        done_button.set_padding(0, 10, 0, 0)
        box.pack_start(title.container, False, False, 0)
        box.pack_start(done_button.align, False, False, 0)

    win.add(box)
    box.show_all()


def update(widget, event):
    global win, box

    win.remove(box)
    win.pack_grid()
    win.update()
    gender.activate(win, win.box)


def disconnect_handlers():
    global done_button, next_button, login_button

    if done_button is not None:
        done_button.disconnect_handlers()
    if next_button is not None:
        next_button.disconnect_handlers()
    if login_button is not None:
        login_button.disconnect_handlers()


def login_screen(widget, event):
    global win, box

    win.remove(box)
    win.pack_grid()
    win.update()
    login.activate(win, win.box)


def close_window(widget, event):
    disconnect_handlers()
    cursor.arrow_cursor(None, None, win)
    Gtk.main_quit()

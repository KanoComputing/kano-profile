# GetData.py
#
# Copyright (C) 2015-2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This contains the RegistrationScreen form component with all the widgets


import os
import re
from email.utils import parseaddr

from gi.repository import GObject, Gtk

from kano.gtk3.kano_dialog import KanoDialog
from kano.logging import logger

from kano_profile.paths import legal_dir

from kano_registration_gui.LabelledEntry import LabelledEntry
from kano_registration_gui.TermsAndConditions import TermsAndConditions
from kano_registration_gui.cache_functions import cache_data, cache_emails, \
    get_cached_data


def is_email(email):
    if '@' in parseaddr(email)[1]:
        return True
    else:
        return False


def check_username(username):
    """
    Check username only has letters, numbers, - and _
    """
    pattern = r'^[a-zA-Z0-9_\-.]+$'
    match = re.match(pattern, username)
    return match and len(username) >= 3 and len(username) <= 25


def check_password(password):
    """
    Check password contains no whitespace and is minimum
    """
    pattern = r'^\S+$'
    match = re.match(pattern, password)
    return match and len(password) > 5


class DataTemplate(Gtk.EventBox):
    __gsignals__ = {
        'widgets-filled': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'widgets-empty': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self):
        Gtk.EventBox.__init__(self)

        self.width = 250
        self.height = 350
        self.set_size_request(self.width, self.height)
        self.get_style_context().add_class('data_screen')


class GetData(DataTemplate):
    """
    This second class registration box is to get the username,
    password and birthday of the user.
    """

    def __init__(self):
        DataTemplate.__init__(self)

        # Set the birthday to be False by default
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # This data contains the saved username and birthday
        data = self.get_cached_username_and_birthday()
        email = get_cached_data('email')

        self._username = LabelledEntry(_("Username"), data['username'])
        self._username.connect('key-release-event', self.validate_username)
        stay_safe = Gtk.Label(_("Stay safe, don't use your real name."))
        stay_safe.get_style_context().add_class('get_data_label')
        stay_safe.set_alignment(0, 0)
        stay_safe.set_margin_left(30)
        stay_safe.set_margin_bottom(10)

        # Do not fill this in
        self._password = LabelledEntry(_("Password"))
        self._password.connect('key-release-event', self.validate_password)

        self.validate_username()

        self.show_password = Gtk.CheckButton.new_with_label(_("Show password"))
        self.show_password.get_style_context().add_class('show_password')
        self.show_password.connect('toggled', self.make_password_entry_visible)
        self.show_password.set_active(True)
        self.show_password.set_margin_left(30)

        self.email_entry = LabelledEntry(_("Email Address"), email)
        self.email_entry.set_placeholder_text('E.g. johndoe@example.com')
        self.email_entry.connect('key-release-event', self.widgets_full)
        self.secondary_email_entry = None

        self.t_and_cs = TermsAndConditions()
        self.t_and_cs.checkbutton.connect('clicked', self.widgets_full)
        self.t_and_cs.connect('t-and-cs-clicked', self.show_terms_and_conditions)

        box.pack_start(self._username, False, False, 5)
        box.pack_start(stay_safe, False, False, 0)
        box.pack_start(self._password, False, False, 5)
        box.pack_start(self.show_password, False, False, 5)
        box.pack_start(self.email_entry, False, False, 5)
        box.pack_start(self.t_and_cs, False, False, 25)

        box.set_margin_top(20)

        self.add(box)

    @property
    def username(self):
        return self._username

    def make_password_entry_visible(self, widget):
        visibility = self.show_password.get_active()
        self._password.set_visibility(visibility)

    def validate_password(self, widget=None, event=None):
        """
        widget is the password entry
        """
        password = self._password.get_text()
        if len(password) == 0:
            self._password.label_success("")
        elif check_password(password):
            self._password.label_success(_(" looks good!"), 'success')
        else:
            self._password.label_success(_(" is not valid"), 'fail')

        self.widgets_full()

    def validate_username(self, widget=None, event=None):
        username = self._username.get_text()
        if len(username) == 0:
            self._username.label_success("")
        elif check_username(username):
            self._username.label_success("", 'success')
        else:
            self._username.label_success(_(" is invalid"), 'fail')

        self.widgets_full()

    def enable_all(self):
        self.checkbutton.set_sensitive(True)
        self._username.set_sensitive(True)
        self._password.set_sensitive(True)
        self.tc_button.set_sensitive(True)

    def get_widget_data(self):
        data = {}

        data['username'] = self._username.get_text()
        data['password'] = self._password.get_text()
        data['email'] = self.email_entry.get_text()

        return data

    # To be passed to the registration screen
    def save_username_and_birthday(self):
        # Birthday should not strictly be got in entry data
        data = self.get_widget_data()
        cache_data('username', data['username'])

    def cache_emails(self):
        data = self.get_email_entry_data()
        cache_emails(data['email'])

    def get_cached_username_and_birthday(self):
        username = get_cached_data('username')
        return {
            'username': username,
        }

    def get_email_entry_data(self):
        """
        This is the data that is sent to the main window and the
        registration
        """

        data = {}
        data['email'] = self.email_entry.get_text()

        # Cache emails if they are retrieved
        cache_emails(data['email'])
        return data

    def widgets_full(self, widget=None, event=None):

        if self._username.validated and \
           self._password.validated and \
           self.t_and_cs.checkbutton.get_active():

            logger.debug("emitting widgets-full")
            self.emit('widgets-filled')

        else:
            logger.debug("emitting widgets-empty")
            self.emit('widgets-empty')

    def show_terms_and_conditions(self, widget):
        """
        This is the dialog containing the terms and conditions - same as
        shown before creating an account
        """
        window = widget.get_toplevel()

        # TODO: Figure out how/whether the legal text will be translated
        legal_text = ''
        for file in os.listdir(legal_dir):
            with open(legal_dir + file, 'r') as f:
                legal_text = legal_text + f.read() + '\n\n\n'

        kdialog = KanoDialog(
            _("Terms and conditions"),
            "",
            scrolled_text=legal_text,
            parent_window=window
        )
        kdialog.run()

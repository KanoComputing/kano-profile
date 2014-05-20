
from gi.repository import Gtk
import heading
import kano_login.components.cursor as cursor


class KanoDialog():

    def __init__(self, title_text="", heading_text="", callback=None, filename=None):
        self.title_text = title_text
        self.heading_text = heading_text
        self.callback = callback
        self.filename = filename
        self.launch_dialog()

    def launch_dialog(self, widget=None, event=None):
        self.dialog = Gtk.Dialog()
        self.dialog.set_decorated(False)
        self.dialog.set_size_request(300, 100)
        self.dialog.set_resizable(False)
        self.dialog.set_border_width(5)

        content_area = self.dialog.get_content_area()
        background = Gtk.EventBox()
        background.get_style_context().add_class("white")
        content_area.reparent(background)
        self.dialog.add(background)
        self.title = heading.Heading(self.title_text, self.heading_text)
        content_area.pack_start(self.title.container, False, False, 0)
        self.dialog_button = Gtk.Button("EXIT")
        self.dialog_button.get_style_context().add_class("green_button")
        self.dialog_button.connect("button_press_event", self.exit_dialog)
        self.hand_handler = self.dialog_button.connect('enter-notify-event',
                                                       cursor.hand_cursor, self.dialog)
        self.arrow_handler = self.dialog_button.connect('leave-notify-event',
                                                        cursor.arrow_cursor, self.dialog)
        self.dialog_button.connect('button-press-event', cursor.arrow_cursor, self.dialog)
        button_box = Gtk.Box()
        button_box.add(self.dialog_button)
        alignment = Gtk.Alignment(xscale=0, yscale=1, xalign=0.5, yalign=1)
        alignment.add(button_box)

        if self.filename is not None:
            image = Gtk.Image()
            image.set_from_file(self.filename)
            content_area.pack_start(image, False, False, 0)

        content_area.pack_start(alignment, False, False, 10)
        self.dialog.show_all()
        self.dialog.run()

    def exit_dialog(self, widget, event):
        self.dialog.destroy()
        cursor.arrow_cursor(None, None, self.dialog)
        if self.callback is not None:
            self.callback()

    def set_callback(self, callback):
        self.callback = callback
        self.dialog_button.connect("button_press_event", self.exit_dialog)

    def set_text(self, title_text, heading_text):
        self.title_text = title_text
        self.heading_text = heading_text
        self.title.set_text(title_text, heading_text)

    def set_button_text(self, text):
        self.dialog_button.set_label(text)

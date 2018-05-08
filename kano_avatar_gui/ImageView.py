#
# ImageView.py
#
# Copyright (C) 2015 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk


# TODO: Make into a fixed and put the environment behind?
class ImageView(Gtk.Fixed):
    '''This finds the picture of the avatar and displays it onto the EventBox
    '''

    _img = None

    def __init__(self, win):
        Gtk.Fixed.__init__(self)

        # TODO: Make it the width of the environment.  This is a guessimate.
        self.width = 703
        # for now, self.height is unspecified
        self.height = -1
        self.set_size_request(self.width, self.height)

        style = self.get_style_context()
        style.add_class('imageview')

        self._current = None
        self._win = win

        self.show()

    def get_window(self):
        return self._win

    def set_image(self, img_loc):
        if not self._img:
            self._img = Gtk.Image.new_from_file(img_loc)
            self.put(self._img, 0, 0)
            self._img.show()
        else:
            self._img.clear()
            self._img.set_from_file(img_loc)

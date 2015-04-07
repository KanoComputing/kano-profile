import os
from gi.repository import Gtk
from kano.gtk3.apply_styles import apply_styling_to_screen


class SelectMenu(Gtk.EventBox):
    def __init__(self, list_of_names, signal_name):
        # The argument items can be of the form
        #
        # self._items = {
        #
        #   IDENTIFIER1: {
        #       path: IMAGE.png,
        #
        #       # Should this be decided internally?
        #       selected: False
        #   },
        #   IDENTIFIER2: {
        #       ...
        #   }
        # }

        Gtk.EventBox.__init__(self)

        # TODO: remove hardcoding
        css_path = os.path.join(
            os.path.expanduser('~'),
            "kano-profile/media/CSS/avatar_generation.css"
        )

        apply_styling_to_screen(css_path)

        # Initialise self._items
        self._items = {}

        for name in list_of_names:
            self._items[name] = {}
            self._items[name]["selected"] = False

        self._signal_name = signal_name

        # This is the selected_identifier
        self._selected = None
        self.get_style_context().add_class("select_menu")

    def _set_selected(self, identifier):
        '''Sets the selected element in the dictionary to True,
        and sets all the others to False
        '''

        self._selected = identifier

        # Old version
        # Unselect current one
        # selected_identifier = self.get_selected()
        # if selected_identifier:
        #    self._items[selected_identifier]['selected'] = False
        # self._items[identifier]['selected'] = True
        # self._only_style_selected(identifier)

    def get_selected(self):
        '''Gets the name of the current selected image
        '''

        return self._selected

        # Old version
        # for identifier, item_info in self._items.iteritems():
        #    if item_info['selected']:
        #        return identifier

    def _unselect_all(self):
        '''Remove all styling on all images, and sets the 'selected'
        field to False
        '''
        # Alternative?
        self._selected = None

        # Old version
        # for item in self._items:
        #    item['selected'] = False
        # Remove all styling
        # self._only_style_selected(None)

    def _add_option_to_items(self, identifier, name, item):
        '''Adds a new option in the self._items
        '''

        if identifier in self._items:
            self._items[identifier][name] = item

    def _add_selected_css(self, button):
        style = button.get_style_context()
        style.add_class("selected")

    def _remove_selected_css(self, button):
        style = button.get_style_context()
        style.remove_class("selected")

    def _add_selected_image(self, button, identifier):
        '''Pack the selected image into the button
        '''
        if 'active_path' in self._items[identifier]:
            path = self._items[identifier]["active_path"]
            image = Gtk.Image.new_from_file(path)
            button.set_image(image)

    def _remove_selected_image(self, button, identifier):
        '''Pack the grey unselected image into the button
        '''
        if 'inactive_path' in self._items[identifier]:
            path = self._items[identifier]["inactive_path"]
            image = Gtk.Image.new_from_file(path)
            button.set_image(image)

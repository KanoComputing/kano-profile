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

        # Initialise self.__items
        self._items = {}

        for name in list_of_names:
            self._items[name] = {}
            self._items[name]["selected"] = False

        self._signal_name = signal_name

    def _selected_image_cb(self, widget, identifier):
        '''This is connected to the button-release-event when you click on a
        button in the table.
        If the image is unlocked, add the css selected class, select the image
        and emit a signal that the parent window can use
        '''

        self._set_selected(identifier)

        # When an image is selected, emit a signal giving the
        # idenitifer as information
        self.emit(self._signal_name, identifier)

    def _set_selected(self, identifier):
        '''Sets the selected element in the dictionary to True,
        and sets all the others to False
        '''

        # Unselect current one
        selected_identifier = self.get_selected()
        if selected_identifier:
            self._items[selected_identifier]['selected'] = False

        self._items[identifier]['selected'] = True
        self._add_selected_css_class(identifier)

    def get_selected(self):
        '''Gets the name of the current selected image
        '''
        for identifier, item_info in self._items.iteritems():
            if item_info['selected']:
                return identifier

    def _unselect_all(self):
        '''Remove all styling on all images, and sets the 'selected'
        field to False
        '''

        for item in self._items:
            item['selected'] = False

        # Remove all styling
        self._add_selected_css_class(None)

    def _add_option_to_items(self, identifier, name, item):
        '''Adds a new option in the self._items
        '''

        if identifier in self._items:
            self._items[identifier][name] = item

    def _add_selected_css_class(self, identifier):
        '''Adds the CSS class that shows the image that has been selected,
        even when the mouse is moved away.
        If identifier is None, will remove all styling
        '''

        for name, img_dict in self._items.iteritems():
            if 'button' in img_dict:
                button = img_dict['button']
                style = button.get_style_context()
                style.remove_class("selected")

        if identifier in self._items:
            if 'button' in self._items[identifier]:
                button = self._items[identifier]['button']
                style = button.get_style_context()
                style.add_class("selected")

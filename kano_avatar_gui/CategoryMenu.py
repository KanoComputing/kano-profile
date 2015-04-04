
from gi.repository import Gtk, GObject
from kano_avatar_gui.SelectMenu import SelectMenu


class CategoryMenu(SelectMenu):

    __gsignals__ = {
        'category_item_selected': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, parser):

        self._item_width = 60
        self._item_height = 60
        self._signal_name = 'category_item_selected'

        self._parser = parser

        # Initialise self._items
        self._items = {}

        # Save the order of the categories so we can use it outside
        self.categories = self._parser.list_available_categories()
        SelectMenu.__init__(self, self.categories, self._signal_name)

        # The menu is one item by 7 items
        self.set_size_request(self._item_width, 7 * self._item_height)

        '''
        for name in cat_names:
            self._items[name] = {}
            self._items[name]["selected"] = False
        '''

        self._pack_buttons()

    def _pack_buttons(self):
        '''Pack the buttons into the menu.
        '''
        # Assume the list of buttons are in self._buttons

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        categories = self._parser.list_available_categories()
        for category in categories:
            button = self._create_button(category)
            self._add_option_to_items(category, 'button', button)
            vbox.pack_start(button, True, True, 0)

    def _create_button(self, identifier):
        '''Create a button with the styling needed for this
        widget.
        We can either pass the dictionary for the whole item,
        or feed in the individual arguments
        '''

        button = Gtk.Button()
        button.set_size_request(60, 60)

        path = self._parser.get_category_icon(identifier)
        icon = Gtk.Image.new_from_file(path)
        button.add(icon)

        button.get_style_context().add_class("category_item")
        button.connect("clicked", self._selected_image_cb,
                       identifier)
        return button

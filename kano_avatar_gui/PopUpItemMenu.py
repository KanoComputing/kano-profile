
from gi.repository import Gtk, GObject
from kano_profile.badges import calculate_badges
from kano_avatar_gui.SelectMenu import SelectMenu


class PopUpItemMenu(SelectMenu):
    '''This creates the pop out menu showing each of the items.
    '''

    __gsignals__ = {
        'pop_up_item_selected': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    # Maybe in the future the items can be read form within the class
    # and they don't need to be passed as arguments
    def __init__(self, category, avatar_parser):

        self._category = category
        self._parser = avatar_parser
        self._signal_name = 'pop_up_item_selected'

        obj_names = self._parser.get_avail_objs(self._category)
        SelectMenu.__init__(self, obj_names, self._signal_name)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        # Grid which the buttons are packed into
        self._grid = Gtk.Grid()

        # Labels the category
        top_bar = self._create_top_bar()
        vbox.pack_start(top_bar, False, False, 0)
        vbox.pack_start(self._grid, False, False, 0)

        self._pack_items()
        # self.connect('pop_up_item_selected', self.print_event)

        self.show_all()

    def print_event(self, arg1, arg2):
        print "arg1 = {}".format(arg1)
        print "arg2 = {}".format(arg2)

    def _create_top_bar(self):
        top_bar = Gtk.EventBox()
        top_bar.get_style_context().add_class("pop_up_menu_top_bar")
        label = Gtk.Label(self._category)
        label.set_alignment(0, 0.5)
        label.set_margin_left(20)
        top_bar.add(label)
        top_bar.set_size_request(150, 40)
        return top_bar

    ##############################################################
    # There is no possibility of these functions being similar to
    # CategoryMenu class

    def _pack_items(self):
        '''Pack the buttons into the menu.
        '''

        # Assume the list of buttons are in self._buttons
        # Pack buttons into a grid

        # There are 2 columns and 5 rows.
        total_rows = 5

        # These are the counters to keep track of where we are
        # in the grid.
        row = 0
        column = 0

        obj_names = self._parser.get_avail_objs(self._category)

        for name in obj_names:
            button = self._create_button(name)
            self._add_option_to_items(name, 'button', button)

            self._grid.attach(button, column, row, 1, 1)
            row += 1

            if row % total_rows == 0:
                row = 0
                column += 1

            # For now, we assume that none of the menus with
            # need more than 2 columns

    #####################################################################
    # These may not be needed depending on the assets given

    def _create_button(self, obj_name):
        '''This places the image onto a Gtk.Fixed so we can overlay a padlock
        on top (if the item is locked)
        This is then put onto a Gtk.Button with the appropriate CSS class.
        Returns the button.

        Hopefully this can be simplified with new assets
        '''

        # Create the container for the thumbnails
        container = Gtk.Fixed()

        path = self._parser.get_item_preview(obj_name)
        image = Gtk.Image.new_from_file(path)
        container.put(image, 0, 0)

        button = Gtk.Button()
        button.get_style_context().add_class('pop_up_menu_item')
        button.add(container)
        image.set_padding(3, 3)
        button.connect('clicked', self._selected_image_cb, obj_name)
        return button


def get_environment_dict():
    return calculate_badges()['environments']['all']


def order_environments():
    environments = get_environment_dict()
    environment_list = []

    # Put the unlocked items first
    for name, item in environments.iteritems():
        if item['achieved']:
            environment_list.append(item)

    for name, item in environments.iteritems():
        if not item['achieved']:
            environment_list.append(item)

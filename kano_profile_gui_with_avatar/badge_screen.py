import os
from gi.repository import Gtk
from kano_profile_gui_with_avatar.SelectionTableItem import BadgeItem
from kano_profile_gui_with_avatar.backend import create_item_page_list
from kano_profile_gui.paths import media_dir


class BadgeScreen(Gtk.EventBox):

    def __init__(self, win):
        Gtk.EventBox.__init__(self)

        self._win = win

        self.badge_grid = BadgeGrid()
        bottom_bar = self._create_bottom_navigation_bar()

        self._win.pack_in_main_content(self.badge_grid)
        self._win.pack_in_bottom_bar(bottom_bar)

    def _create_bottom_navigation_bar(self):
        bottom_bar = Gtk.Box()

        self.next_button = self._create_navigation_button("NEXT PAGE")
        self.prev_button = self._create_navigation_button("PREVIOUS")

        bottom_bar.pack_start(self.next_button, False, False, 0)
        bottom_bar.pack_start(self.prev_button, False, False, 0)
        return bottom_bar

    def _create_navigation_button(self, title):
        hbox = Gtk.Box()
        label = Gtk.Label(title)
        button = Gtk.Button()
        button.get_style_context().add_class("navigation-button")

        if title == "PREVIOUS":
            # path is for previous icon
            prev_path = ''
            icon = Gtk.Image(prev_path)
            hbox.pack_start(icon, False, False, 0)
            hbox.pack_start(label, False, False, 0)
            button.connect("clicked", self._change_page, -1)

        elif title == "NEXT PAGE":
            # path is for next icon
            next_path = ''
            icon = Gtk.Image(next_path)
            hbox.pack_start(label, False, False, 0)
            hbox.pack_start(icon, False, False, 0)
            button.connect("clicked", self._change_page, 1)

        button.add(hbox)
        return button

    def _load_page(self, widget, page_increment):
        self._page += page_increment
        self.badge_grid.load_page(self._page)

    def _create_badge_button(self, name, path):
        button = Gtk.Button()
        image = Gtk.Image.new_from_file(path)

        # It's probably a lot more complicated than this as we need to style the buttons
        # and have a hover over label
        button.add(image)
        # check button order?


class BadgeGrid(Gtk.Grid):
    def __init__(self, page):
        Gtk.Grid.__init__(self)

        '''
        GtkGrid *grid,
                 GtkWidget *child,
                 gint left,
                 gint top,
                 gint width,
                 gint height)
        '''

        # Not sure if you need this
        self._page = page

    def _split_info_into_pages(self):
        self.badge_list, self.page_list = create_item_page_list()

    def _pack_badge_grid(self, page_number):
        badge_list = self.page_list[page_number]

        for badge_info in badge_list:
            row = badge_list['row']
            column = badge_list['column']
            badge_widget = BadgeItem(badge_info)
            self.attach(badge_widget, row, column, 1, 1)

    def _unpack_badge_grid(self):
        for child in self.get_children():
            self.remove(child)

    def load_page(self, page):
        self._unpack_badge_grid()
        self._pack_badge_grid(page)


class BadgeInfoScreen(Gtk.EventBox):
    '''This screen shows the large version of the badge image,
    the title and the description
    '''

    def __init__(self, win, item_list, index):
        '''
        item_info is the dictionary of the selected item
        item_list is the ordered list of badges
        '''

        self._win = win

        # these are the data structures
        self.item_list = item_list
        self.index = index

        self.item_info = self.item_list[index]

        # set the background of the badge part to the colour
        # described by the item_info
        self._create_bottom_navigation_bar()

    # TODO: move this outside, or get this from inheritance,
    # as this is the same height across all screens
    def _create_bottom_navigation_bar(self):
        bottom_bar = Gtk.Box()

        self.next_button = self._create_navigation_button("previous")
        self.prev_button = self._create_navigation_button("middle")
        self.grid_button = self._create_navigation_button("end")

        bottom_bar.pack_start(self.prev_button, False, False, 0)
        bottom_bar.pack_start(self.grid_button, False, False, 0)
        bottom_bar.pack_start(self.next_button, False, False, 0)

        self._win.pack_in_bottom_bar(bottom_bar)

    def _create_navigation_button(self, title, position='previous'):
        '''position is either 'previous', 'middle' or 'end'
        This is to determine the position of the icon on the button
        '''
        hbox = Gtk.Box()
        button = Gtk.Button()
        button.get_style_context().add_class("navigation-button")

        # If the button is at the end, the icon comes after the label
        if position == "end":
            # path is for next icon
            next_path = ''
            icon = Gtk.Image(next_path)

            # get title of end button
            title = self.item_list[self.index + 1]["title"].upper()
            label = Gtk.Label(title)

            hbox.pack_start(label, False, False, 0)
            hbox.pack_start(icon, False, False, 0)
            button.connect("clicked", self._change_page, 1)

        # Otherwise if the icon is at the middle or start,
        # the icon comes before the text
        else:
            if position == "previous":
                # get previous icon path
                path = ''
                title = self.item_list[self.index + 1]["title"].upper()
                label = Gtk.Label(title)
                button.connect("clicked", self._go_to_other_badge, -1)

            elif position == "middle":
                # path is for middle icon
                path = ''
                title = "BACK TO GRID"
                label = Gtk.Label(title)
                button.connect("clicked", self._go_to_grid)

            icon = Gtk.Image(path)
            hbox.pack_start(icon, False, False, 0)
            hbox.pack_start(label, False, False, 0)

        button.add(hbox)
        return button

    def _go_to_other_badge(self, widget, change_index):
        # we know the index of the current widget, so we
        # need to change the index, get the new selected,
        # unpack the current widgets and pack the new widgets
        self._win.unpack_bottom_bar()
        self._win.unpack_main_content()
        new_index = self.index + change_index
        BadgeInfoScreen(self._win, self.item_info, new_index)

    def _go_to_grid(self, widget):
        self._win.unpack_bottom_bar()
        self._win.unpack_main_content()
        BadgeScreen(self._win)

    def _get_item_colour(self):
        return self.item_info['bg_color']

    def _get_image_path_at_size(self, width, height):
        size_dir = str(width) + 'x' + str(height)
        category = self.item_info['category']
        name = self.item_info['name']
        locked = self.item_info['locked']

        if locked:
            name = name + "_locked"

        path = os.path.join(media_dir, size_dir, category, name + '.png')
        return path

    def set_image_from_info(self, width, height):
        img_path = self._get_image_path_at_size(590, 270)
        self.image = Gtk.Image.new_from_file(img_path)

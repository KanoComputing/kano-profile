import os
from gi.repository import Gtk, Gdk, Pango
from kano_profile_gui_with_avatar.SelectionTableItem import BadgeItem
from kano_profile_gui_with_avatar.backend import create_item_page_list
from kano_profile_gui.paths import media_dir


class BadgeScreen(Gtk.EventBox):

    def __init__(self, win):
        Gtk.EventBox.__init__(self)

        self._win = win
        self._page = 0

        self.badge_grid = BadgeGrid(win)
        bottom_bar = self._create_bottom_navigation_bar()

        self._win.pack_in_main_content(self.badge_grid)
        self._win.pack_in_bottom_bar(bottom_bar)
        self._load_page()

        self._win.show_all()

    def _create_bottom_navigation_bar(self):
        bottom_bar = Gtk.Box()

        self.next_button = self._create_navigation_button("NEXT PAGE")
        self.prev_button = self._create_navigation_button("PREVIOUS")

        bottom_bar.pack_start(self.prev_button, False, False, 0)
        bottom_bar.pack_end(self.next_button, False, False, 0)
        return bottom_bar

    def _create_navigation_button(self, title):
        hbox = Gtk.Box()
        label = Gtk.Label(title)
        button = Gtk.Button()
        button.get_style_context().add_class("navigation_button")

        if title == "PREVIOUS":
            # path is for previous icon
            button.get_style_context().add_class("back")
            prev_arrow_path = os.path.join(media_dir, "images/icons/previous.png")
            icon = Gtk.Image.new_from_file(prev_arrow_path)
            hbox.pack_start(icon, False, False, 0)
            hbox.pack_start(label, False, False, 0)
            button.connect("clicked", self._load_page_wrapper, -1)

        elif title == "NEXT PAGE":
            # path is for next icon
            button.get_style_context().add_class("next")
            next_arrow_path = os.path.join(media_dir, "images/icons/next.png")
            icon = Gtk.Image.new_from_file(next_arrow_path)
            hbox.pack_start(label, False, False, 0)
            hbox.pack_start(icon, False, False, 0)
            button.connect("clicked", self._load_page_wrapper, 1)

        button.add(hbox)
        return button

    def _load_page_wrapper(self, widget, page_increment):
        self._page += page_increment
        self._load_page()

    def _load_page(self):
        self.badge_grid.load_page(self._page)
        self._enable_next_prev_button()
        self._win.show_all()

    def _enable_next_prev_button(self):
        max_page_number = self.badge_grid.get_number_of_pages()

        if self._page == 0:
            self.prev_button.set_sensitive(False)
            self.next_button.set_sensitive(True)
        elif self._page == max_page_number - 1:
            self.prev_button.set_sensitive(True)
            self.next_button.set_sensitive(False)
        else:
            self.prev_button.set_sensitive(True)
            self.next_button.set_sensitive(True)

    def _create_badge_button(self, name, path):
        button = Gtk.Button()
        image = Gtk.Image.new_from_file(path)

        # It's probably a lot more complicated than this as we need to
        # style the buttons and have a hover over label
        button.add(image)
        # check button order?


class BadgeGrid(Gtk.Grid):
    def __init__(self, win):
        Gtk.Grid.__init__(self)
        self._win = win
        self._item_width = 230
        self._item_height = 180

        self._split_info_into_pages()
        # self._pack_badge_grid(1)

    def get_number_of_pages(self):
        return len(self.page_list)

    def _split_info_into_pages(self):
        self.badge_list, self.page_list = create_item_page_list()

    def _pack_badge_grid(self, page_number):
        badge_list = self.page_list[page_number]

        for i in range(len(badge_list)):
            badge_info = badge_list[i]

            row = badge_info['row']
            column = badge_info['column']

            category = badge_info['category']
            name = badge_info["name"]
            title = badge_info["title"]
            desc_unlocked = badge_info["desc_unlocked"]
            desc_locked = badge_info["desc_locked"]
            background_colour = badge_info['bg_color']
            locked = not badge_info['achieved']

            image_path = get_image_path_at_size(
                category, name, locked,
                self._item_width, self._item_height
            )

            badge_widget = BadgeItem(
                image_path, title, desc_unlocked, desc_locked,
                background_colour, locked
            )

            # This is the index of the badge in the ordered array of all the badges
            index = page_number * 6 + i
            badge_widget.connect("clicked", self._go_to_badge_info_wrapper, index)
            self.attach(badge_widget, column, row, 1, 1)

    def _go_to_badge_info_wrapper(self, widget, index):
        self._go_to_badge_info(index)

    def _go_to_badge_info(self, index):
        self._win.empty_main_content()
        self._win.empty_bottom_bar()
        BadgeInfoScreen(self._win, self.badge_list, index)

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
        self.image_width = 460
        self.image_height = 448

        # these are the data structures
        self.item_list = item_list
        self.index = index

        self.item_info = self.item_list[index]

        self._show_badge()
        # set the background of the badge part to the colour
        # described by the item_info
        self._create_bottom_navigation_bar()
        self._win.show_all()

    def _show_badge(self):
        background = Gtk.EventBox()

        locked = not self.item_info['achieved']
        if locked:
            color = Gdk.RGBA()
            color.parse('#dddddd')
        else:
            bg_color = self.item_info['bg_color']
            color = Gdk.RGBA()
            color.parse('#' + bg_color)

        background.override_background_color(Gtk.StateFlags.NORMAL,
                                             color)

        category = self.item_info['category']
        name = self.item_info['name']

        filename = get_image_path_at_size(
            category, name, locked, self.image_width, self.image_height
        )
        self.image = Gtk.Image.new_from_file(filename)
        info_box = self._create_info_box()

        hbox = Gtk.Box()
        hbox.pack_start(self.image, False, False, 0)
        hbox.pack_start(info_box, False, False, 0)

        background.add(hbox)

        self._win.pack_in_main_content(background)

    def _create_info_box(self):
        info_box = Gtk.EventBox()
        info_box.get_style_context().add_class("info_box")

        title = self.item_info["title"]
        locked = not self.item_info['achieved']

        if locked:
            description = self.item_info["desc_locked"]
        else:
            description = self.item_info["desc_unlocked"]

        title_label = Gtk.Label(title, xalign=0)
        title_label.get_style_context().add_class("info_heading")

        description_label = Gtk.Label(description, xalign=0)
        description_label.get_style_context().add_class("info_paragraph")
        description_label.set_line_wrap(True)
        description_label.set_line_wrap_mode(Pango.WrapMode.WORD)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(title_label, False, False, 10)
        vbox.pack_start(description_label, False, False, 10)
        vbox.set_margin_left(20)
        vbox.set_margin_left(20)
        vbox.set_margin_top(20)

        info_box.add(vbox)

        return info_box

    # TODO: move this outside, or get this from inheritance,
    # as this is the same height across all screens
    def _create_bottom_navigation_bar(self):
        bottom_bar = Gtk.ButtonBox()

        self.prev_button = self._create_navigation_button("previous")
        self.grid_button = self._create_navigation_button("middle")
        self.next_button = self._create_navigation_button("end")

        bottom_bar.pack_start(self.prev_button, False, False, 0)
        bottom_bar.pack_start(self.grid_button, False, False, 0)
        bottom_bar.pack_end(self.next_button, False, False, 0)

        self._win.pack_in_bottom_bar(bottom_bar)

    def _create_navigation_button(self, position='previous'):
        '''position is either 'previous', 'middle' or 'end'
        This is to determine the position of the icon on the button
        '''
        hbox = Gtk.Box()
        button = Gtk.Button()
        button.get_style_context().add_class("navigation_button")

        # If the button is at the end, the icon comes after the label
        if position == "end":
            # path is for next icon
            next_icon_path = os.path.join(media_dir, "images/icons/next.png")
            icon = Gtk.Image.new_from_file(next_icon_path)
            button.get_style_context().add_class("next")

            # get title of end button
            title = self.item_list[self.index + 1]["title"].upper()
            label = Gtk.Label(title)

            hbox.pack_start(label, False, False, 0)
            hbox.pack_start(icon, False, False, 0)
            button.connect("clicked", self._go_to_other_badge, 1)

        # Otherwise if the icon is at the middle or start,
        # the icon comes before the text
        else:
            if position == "previous":
                # get previous icon path
                icon_path = os.path.join(media_dir, "images/icons/next.png")
                title = self.item_list[self.index - 1]["title"].upper()
                label = Gtk.Label(title)
                button.connect("clicked", self._go_to_other_badge, -1)
                button.get_style_context().add_class("back")

            elif position == "middle":
                # path is for middle icon
                icon_path = os.path.join(media_dir, "images/icons/grid.png")
                title = "BACK TO GRID"
                label = Gtk.Label(title)
                button.connect("clicked", self._go_to_grid)
                button.get_style_context().add_class("middle")

            icon = Gtk.Image.new_from_file(icon_path)
            hbox.pack_start(icon, False, False, 0)
            hbox.pack_start(label, False, False, 0)

        button.add(hbox)
        return button

    def _go_to_other_badge(self, widget, change_index):
        # we know the index of the current widget, so we
        # need to change the index, get the new selected,
        # unpack the current widgets and pack the new widgets
        self._win.empty_bottom_bar()
        self._win.empty_main_content()
        new_index = self.index + change_index
        BadgeInfoScreen(self._win, self.item_list, new_index)

    def _go_to_grid(self, widget):
        self._win.empty_bottom_bar()
        self._win.empty_main_content()
        BadgeScreen(self._win)

    def _get_item_colour(self):
        return self.item_info['bg_color']

    def set_image_from_info(self, width, height):
        img_path = self._get_image_path_at_size(590, 270)
        self.image = Gtk.Image.new_from_file(img_path)


def get_image_path_at_size(category, name, locked, width, height):
    size_dir = str(width) + 'x' + str(height)

    if locked:
        name = name + "_locked"

    path = os.path.join(media_dir, "images", "badges", size_dir, category, name + '.png')
    return path

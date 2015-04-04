
import os
import sys
from gi.repository import Gtk, GObject

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)
        print dir_path

from kano_avatar_gui.PopUpItemMenu import PopUpItemMenu
from kano_avatar_gui.CategoryMenu import CategoryMenu
# from kano_avatar.logic import AvatarConfParser
# from kano_avatar.logic import get_avatar_conf
from kano.gtk3.application_window import ApplicationWindow


class Menu(Gtk.Fixed):

    __gsignals__ = {
        'asset_selected': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, parser):
        Gtk.Fixed.__init__(self)

        self._parser = parser
        self._cat_menu = CategoryMenu(self._parser)
        self._cat_menu.connect('category_item_selected',
                               self.launch_pop_up_menu)

        self.put(self._cat_menu, 0, 0)

        self.menus = {}
        # self.connect('asset_selected', self.__print_event)

        for category in self._cat_menu.categories:
            self.menus[category] = {}

        self.show_all()

    def get_selected_category(self):
        return self._cat_menu.get_selected()

    def get_selected_obj(self, category):
        if "menu" in self.menus[category]:
            return self.menus[category]["menu"].get_selected()
        else:
            return ""

    def get_all_selected_objs(self):
        objs = []
        for category in self._cat_menu.categories:
            selected_obj = self.get_selected_obj(category)
            if selected_obj:
                objs.append(selected_obj)

        return objs

    def __print_event(self, arg1, arg2):
        print "Menu"
        print "arg1 = {}".format(arg1)
        print "arg2 = {}".format(arg2)
        print "\n"
        # return False

    def launch_pop_up_menu(self, widget, category):

        self._hide_menus()
        index = self._cat_menu.categories.index(category)
        y_position = index * 100

        if "menu" not in self.menus[category]:
            menu = PopUpItemMenu(category, self._parser)

            # Propagate signal up
            menu.connect('pop_up_item_selected', self._emit_signal)

            self.menus[category]["menu"] = menu
            self.put(self.menus[category]['menu'],
                     100, y_position)
            self.menus[category]['menu'].show()
        else:
            self.menus[category]["menu"].show()

    def _hide_menus(self):
        for category, menu_dict in self.menus.iteritems():

            if "menu" in self.menus[category]:
                self.menus[category]["menu"].hide()

    def _emit_signal(self, widget, category):
        '''This is to propagate the signal the signal up a widget
        '''
        self.emit('asset_selected', category)


class ExampleWindow(ApplicationWindow):

    def __init__(self):
        ApplicationWindow.__init__(self, "draft", 400, 400)
        self.menu = Menu()
        self.set_main_widget(self.menu)
        self.show_all()


if __name__ == "__main__":
    ExampleWindow()
    Gtk.main()

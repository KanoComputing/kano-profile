

import os
from gi.repository import Gtk, GdkPixbuf
from kano_profile.apps import load_app_state_variable, save_app_state_variable
from kano.notifications import display_generic_notification


class MissionScreen(Gtk.Box):
    egg_path = os.path.join(
        os.path.expanduser("~"),
        "content/egg.png"
    )
    cracked_egg_path = os.path.join(
        os.path.expanduser("~"),
        "content/cracked-egg.png"
    )
    hatched_path = os.path.join(
        os.path.expanduser("~"),
        "content/hatched.png"
    )

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.image = Gtk.Image()
        self.title = Gtk.Label()
        self.pack_start(self.title, False, False, 10)
        self.pack_start(self.image, False, False, 20)
        self._win = win
        self._win.pack_in_main_content(self)
        self.read_and_show_stage()
        self._win.show_all()

    def read_and_show_stage(self):
        stage = self.read_egg_stage()
        self.show_stage(stage)

    @staticmethod
    def read_egg_stage():
        return load_app_state_variable("kano-egg", "level")

    @staticmethod
    def save_egg_level(stage, level):
        save_app_state_variable("kano-egg", "level", level)
        MissionScreen.show_egg_notification()

    @staticmethod
    def show_egg_notification():
        stage = MissionScreen.read_egg_stage()

        if stage in [1, 2]:
            # Needs to be 280 by 170
            stage_info = {
                1: {
                    "title": "The egg is cracking!",
                    "byline": "",
                    "img_path": MissionScreen.cracked_egg_path
                },
                2: {
                    "title": "The egg has hatched!",
                    "byline": "You can now see your kreature next to your kharacter!",
                    "img_path": MissionScreen.hatched_path
                }
            }

            title = stage_info[stage]["title"]
            byline = stage_info[stage]["byline"]
            path = stage_info[stage]["img_path"]

            display_generic_notification(title, byline, path)

    def show_stage(self, stage):

        # stage 0 is uncracked
        # stage 1 is cracked
        if not stage:
            if stage is None:
                save_app_state_variable("kano-egg", "level", 0)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.egg_path, -1, 300)
            self.title.set_text("It will only hatch if you're more active")
        elif stage == 1:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.cracked_egg_path, -1, 300)
            self.title.set_text("Ooh! It's making noises!")
        elif stage == 2:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.hatched_path, -1, 300)
            self.title.set_text("Congratulations, it's hatched!")

        # Whatever is reasonable
        self.image.set_from_pixbuf(pixbuf)

#!/usr/bin/env python
# PRIME Indicator - indicator applet for NVIDIA Optimus laptops
# Copyright (C) 2013 Alfred Neumayer
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import appindicator
import commands
import gtk
import os


class PRIMEIndicator:

    def __init__(self):
        self.ind = appindicator.Indicator("PRIME Indicator",
                                          "indicator-messages",
                                          appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("indicator-messages-new")
        self.ind.set_icon_theme_path("/usr/lib/primeindicator/")
        self.is_integrated = self.check_integrated()
        self.script = "sudo /usr/lib/primeindicator/gpuswitcher"
        self.config_file = os.getenv(
            "HOME") + "/.config/prime-indicator/use_dark_icons"
        self.switch_icon('intel')
        if self.is_integrated:
            self.turn_nv_off()
        else:
            self.switch_icon('nvidia')
            self.turn_nv_on()
        self.menu_setup()
        self.ind.set_menu(self.menu)

    def menu_setup(self):
        self.menu = gtk.Menu()
        self.info_item = gtk.MenuItem(self.renderer_string())
        self.info_item.set_sensitive(False)
        self.info_item.show()
        self.separator_item = gtk.SeparatorMenuItem()
        self.separator_item.show()
        self.switch_item = gtk.MenuItem("Quick switch graphics ...")
        self.switch_item.connect("activate", self.switch)
        self.switch_item.show()
        self.separator2_item = gtk.SeparatorMenuItem()
        self.separator2_item.show()
        self.info_nvinfo_item = gtk.MenuItem(self.nv_power_string())
        self.info_nvinfo_item.set_sensitive(False)
        self.separator_nvinfo_item = gtk.SeparatorMenuItem()
        self.switch_nvinfo_item = gtk.MenuItem(self.nv_power_switch_string())
        self.switch_nvinfo_item.connect("activate", self.switch_nv_power)
        self.separator2_nvinfo_item = gtk.SeparatorMenuItem()
        if self.is_integrated:
            self.info_nvinfo_item.show()
            self.switch_nvinfo_item.show()
            self.separator_nvinfo_item.show()
            self.separator2_nvinfo_item.show()
        self.icon_item = gtk.MenuItem(
            self.get_switch_icons_label(self.check_dark_icons()))
        self.icon_item.connect("activate", self.invert_icon_color)
        self.icon_item.show()
        self.separator3_item = gtk.SeparatorMenuItem()
        self.separator3_item.show()
        self.settings_item = gtk.MenuItem("Open NVIDIA Settings")
        self.settings_item.connect("activate", self.open_settings)
        self.settings_item.show()
        self.menu.append(self.info_item)
        self.menu.append(self.separator_item)
        self.menu.append(self.switch_item)
        self.menu.append(self.separator2_item)
        self.menu.append(self.info_nvinfo_item)
        self.menu.append(self.separator_nvinfo_item)
        self.menu.append(self.switch_nvinfo_item)
        self.menu.append(self.separator2_nvinfo_item)
        self.menu.append(self.icon_item)
        self.menu.append(self.separator3_item)
        self.menu.append(self.settings_item)

    def get_switch_icons_label(self, icon_dark=False):
        return "Switch to " + ("light" if icon_dark else "dark") + " icons"

    def switch(self, dude):
        response = self.show_reboot_dialog()
        if response != gtk.RESPONSE_CANCEL:
            self.switch_gpu()
            self.logout()

    def invert_icon_color(self, dude):
        self.switch_icon_color(
            self.ind.get_icon(), not self.check_dark_icons())

    def switch_icon(self, icon_name):
        self.switch_icon_color(icon_name, self.check_dark_icons())

    def switch_icon_color(self, icon_name, icon_dark=False):
        if not os.path.exists(os.path.dirname(self.config_file)):
            try:
                os.makedirs(os.path.dirname(self.config_file))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        with open(self.config_file, "w") as f:
            if icon_dark:
                if not icon_name.endswith("dk"):
                    icon_name += "dk"
                f.write("true")
            else:
                if icon_name.endswith("dk"):
                    icon_name = icon_name[:-2]
                f.write("false")
        self.ind.set_icon(icon_name)
        try:
            self.icon_item.set_label(self.get_switch_icons_label(icon_dark))
        except AttributeError:
            pass

    def check_dark_icons(self):
        icon_dark = False
        if not os.path.exists(os.path.dirname(self.config_file)):
            try:
                os.makedirs(os.path.dirname(self.config_file))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        if os.path.isfile(self.config_file):
            with open(self.config_file, "r") as f:
                icon_dark = (f.readline().lower().strip() == "true")
        return icon_dark

    def open_settings(self, dude):
        os.system("/usr/bin/nvidia-settings")

    def show_reboot_dialog(self):
        message = "You will be logged out now."
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO,
                                   gtk.BUTTONS_NONE, message)
        dialog.set_deletable(False)
        dialog.connect('delete_event', self.ignore)
        dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        response = dialog.run()
        dialog.destroy()
        return response

    def ignore(*args):
        return gtk.TRUE

    def check_integrated(self):
        stat, out = commands.getstatusoutput("/usr/bin/prime-select query")
        if "intel" in out:
            return True
        else:
            return False

    def renderer_string(self):
        stat, out = commands.getstatusoutput(
            'glxinfo | grep "OpenGL renderer string"')
        out = out.replace("OpenGL renderer string", "Using")
        return out

    def nv_power_string(self):
        return "NVIDIA GPU is powered " + ("ON" if self.nv_power else "OFF")

    def nv_power_switch_string(self):
        return "Force NVIDIA GPU to power " + ("OFF" if self.nv_power else "ON")

    def is_nvidia_on(self):
        stat, out = commands.getstatusoutput('cat /proc/acpi/bbswitch')
        return out.endswith("ON")

    def switch_gpu(self):
        if self.is_integrated:
            os.system(self.script + " nvidia")
        else:
            os.system(self.script + " intel")

    def switch_nv_power(self, dude):
        if self.nv_power:
            self.turn_nv_off()
        else:
            self.turn_nv_on()

    def turn_nv_off(self):
        os.system(self.script + " nvidia off")
        self.nv_power = self.is_nvidia_on()
        try:
            self.info_nvinfo_item.set_label(self.nv_power_string())
            self.switch_nvinfo_item.set_label(self.nv_power_switch_string())
        except AttributeError:
            pass

    def turn_nv_on(self):
        os.system(self.script + " nvidia on")
        self.nv_power = self.is_nvidia_on()
        try:
            self.info_nvinfo_item.set_label(self.nv_power_string())
            self.switch_nvinfo_item.set_label(self.nv_power_switch_string())
        except AttributeError:
            pass

    def logout(self):
        env = os.environ.get('DESKTOP_SESSION')
        if env == "xubuntu" or env == "xfce4":
            os.system('xfce4-session-logout -l')
        else:
            os.system('gnome-session-quit --logout --no-prompt')

    def main(self):
        gtk.main()

if __name__ == "__main__":
    indicator = PRIMEIndicator()
    indicator.main()
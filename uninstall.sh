#!/bin/bash
# PRIME Indicator - indicator applet for NVIDIA Optimus laptops
# Copyright (C) 2013 Alfred Neumayer
# Copyright (C) 2016 André Brait
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root." 2>&1
    exit 1
fi

rm -f /usr/bin/primeindicator.py
rm -f /etc/sudoers.d/primeindicator-sudoers
rm -f $HOME/.config/autostart/primeindicator.desktop
rm -rf /usr/lib/primeindicator
rm -rf $HOME/.config/primeindicator

echo "Uninstall complete."
exit 0
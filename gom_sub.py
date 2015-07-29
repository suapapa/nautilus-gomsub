#!/usr/bin/python
# -*- coding: utf-8 -*-

# gom_sub.py : search subscript(like smi or srt) on the Gom Subtitle PDS;
# http://gom.gomtv.com/jmdb/index.html
#
# Copyright (C) 2010-2015 by Homin Lee <homin.lee@suapapa.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os
import sys
import urllib
import webbrowser


GOM_SUB_ADDR = "http://gom.gomtv.com/main/index.html?ch=subtitles&pt=l&menu=subtitles&lang=0&sValue=%s"


HAS_NAUTILUS = True
try:
    # install python-nautilus package;
    #     $ sudo apt-get install python-nautilus
    # place this script under ~/.local/share/Nautilus-python/extensions/
    #     $ mkdir -p ~/.local/share/nautilus-python/extensions
    #     $ cp gom_sub.py ~/.local/share/nautilus-python/extensions/
    from gi.repository import Nautilus, GObject
except:
    # maybe we run this script on terminal
    HAS_NAUTILUS = False


def _querySub(searchKey):
    return GOM_SUB_ADDR%\
        urllib.quote_plus(searchKey)


def searchGomSubPDS(movieName):
    print movieName
    if not movieName.rfind('.') == -1:
        movieName = movieName[:movieName.rfind('.')] # chop the ext.

    # increase the chance
    movieName = movieName.replace('.', ' ')
    movieName = movieName.replace('_', ' ')
    movieName = movieName.replace('-', ' ')

    sl = movieName.split()
    while sl:
        queryAddr = _querySub(' '.join(sl))
        tempSite = urllib.urlopen(queryAddr)
        tempDoc = tempSite.read(-1)

        # check if there r any subtitle found.
        if tempDoc.find('<p class="total">총 <span>0</span>개</p>') == -1:
            webbrowser.open(queryAddr)
            return True

        # our search key was too long. let's chop more!
        sl = sl[:-1]

    # we are in trouble :$
    print("Give up! no subtitle found.")
    return False

if HAS_NAUTILUS:
    class GomSubMenuProvider(GObject.GObject, Nautilus.MenuProvider):
        def __init__(self):
            pass

        def menu_activate_cb(self, menu, file):
            if file.is_gone():
                return

            # Strip leading file://
            filename = urllib.unquote(file.get_uri()[7:])
            result = searchGomSubPDS(os.path.basename(filename))
            if not result:
                os.system('zenity --error --title="자막검색" --text="찾지 못했습니다."')

        def get_file_items(self, window, files):
            if len(files) != 1:
                return

            file = files[0]
            if not "video/" in file.get_mime_type():
                 return

            if file.get_uri_scheme() != 'file':
                return

            item = Nautilus.MenuItem(name='Nautilus::search_gom_sub_pds',
                                     label='자막 검색',
                                     tip='곰 자막 자료실 검색',
                                     icon='')
            item.connect('activate', self.menu_activate_cb, file)
            return item,

if __name__ == "__main__":
    try:
        movieName = os.path.basename(sys.argv[1])
    except IndexError:
        print "Usage: %s [the_movie_file_name]"%sys.argv[0]
        sys.exit(1)

    if searchGomSubPDS(movieName):
        sys.exit(0)
    else:
        sys.exit(1)

# vim: et sw=4

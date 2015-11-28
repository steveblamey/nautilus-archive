# coding: utf-8
#
# Copyright 2013 Steve Blamey
#
# This file is part of Nautilus-archive.
#
# Nautilus-archive is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Nautilus-archive is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nautilus-archive. If not, see <http://www.gnu.org/licenses/>.
#

import gi
gi.require_version('Nautilus', '3.0')

from gi.repository import Nautilus, GObject, Gtk, Gdk, Gio
from trackertag import TrackerTag
import os
import datetime

class ColumnExtension(GObject.GObject, Nautilus.MenuProvider, Nautilus.InfoProvider, Nautilus.LocationWidgetProvider):
    def __init__(self):
        print("Initializing nautilus-archive")
        self.tracker = TrackerTag()
        self.archive_folder = Gio.file_new_for_path(os.path.join(os.getenv("HOME"), "Archive"))
        self.tag_settings = {
            'archive': ('emblem-package', self.archive_folder.get_uri()),
            'test': ('emblem-generic', self.archive_uri_join('Work')),
            #'project': ('emblem-generic', self.archive_uri_join('Project')),
        }
        
        #create Archive folder
        if not self.archive_folder.query_exists(None):
            self.archive_folder.make_directory(None)

        # set folder icon
        self.archive_folder.set_attribute_string("metadata::custom-icon-name", 'folder-documents', Gio.FileQueryInfoFlags.NONE, None)

        #create sub-folders and tracker tags
        for tag, settings in self.tag_settings.items():
            folder = Gio.file_new_for_uri(settings[1])
            if not folder.query_exists(None) and tag != 'archive':
                folder.make_directory(None)
            if not self.tracker.tag_exists(tag):
                self.tracker.new_tag(tag)

    def archive_uri_join(self, *args):
        segments = (self.archive_folder.get_uri(),) + (args)
        return "/".join(map(str, segments))

    def get_widget(self, uri, window):
        #Only show archive bar in the Archive directory
        if uri == self.archive_folder.get_uri():
            
            tags = tuple(tag for tag in self.tag_settings)
            tagged_uris = self.tracker.tagged_files(tags)
            if tagged_uris:
                button_msg = "Archive %s Files" % len(tagged_uris)
            else:
                button_msg = "Nothing to Archive"
            
            archive_bar = Gtk.Box(spacing=6)
            archive_bar.set_name('archive-bar')
            
            main_glabel = Gtk.Label()
            main_glabel.set_markup('<b>Archive</b>')
            main_glabel.set_name('archive-label')
            
            archive_gbutton = Gtk.Button(button_msg)
            archive_gbutton.set_name('archive-button')
            archive_gbutton.set_tooltip_text("Move all tagged files to the Archive folder")
            #Deactivate archive button if no files are tagged
            if not tagged_uris:
                archive_gbutton.set_sensitive(False)
            archive_gbutton.connect("clicked", self.on_archive_gbutton_clicked, window)
            archive_gbutton.set_relief(Gtk.ReliefStyle.HALF)
            archive_button = Gtk.ButtonBox()
            archive_button.set_border_width(6)
            archive_button.add(archive_gbutton)
            
            archive_bar.pack_end(archive_button, False, False, 0)
            
            background_box = Gtk.InfoBar()
            background_box.add(archive_bar)
            background_box_content = background_box.get_content_area()
            background_box_content.add(main_glabel)
            background_box.show_all()
            return background_box
        else:
            return
        
    def on_archive_gbutton_clicked(self, button, window):
        tags = [tag for tag in self.tag_settings]
        for tag in tags:
            file_uris = self.tracker.tagged_files(tag)
            if file_uris:
                errors = 0
                for f in file_uris:
                    try:
                        source_file = Gio.file_new_for_uri(f)
                        target_file = Gio.file_new_for_uri("/".join((self.tag_settings[tag][1], source_file.get_basename())))
                        tag_removed = self.tracker.remove_tag(f, tag)
                        if tag_removed:
                            source_file.move(target_file, Gio.FileCopyFlags.NONE, None, None, None)
                            button.set_sensitive(False)
                            button.set_label("Nothing to Archive")
                        else:
                            raise Exception("Unable to remove tag")
                        
                    except:
                        self.tracker.add_tag(f, tag)
                        errors +=1
                        raise

                if errors:
                    dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "No Files Archived")
                    dialog.format_secondary_text("There was an error when trying to move $s files to the archive" % errors)
                    dialog.run()
                    dialog.destroy()
    
    def update_file_info_full(self, provider, handle, closure, file):
        # Some dropbox folder cause the mess below with cpu @100% :
        #File "/usr/share/nautilus-python/extensions/nautilus-archive.py", line 162, in update_emblem
        #    if self.tracker.has_tag(file.get_uri(), tag):
        #  File "/usr/local/lib/python2.7/dist-packages/trackertag.py", line 61, in has_tag
        #    cursor = self.connection.query (squery, None)
        #  File "/usr/lib/python2.7/dist-packages/gi/types.py", line 113, in function
        #    return info.invoke(*args, **kwargs)
        #gi._glib.GError: 1.86: syntax error, expected `}'
        #Traceback (most recent call last):
        #  File "/usr/lib/python2.7/dist-packages/gi/overrides/GLib.py", line 629, in <lambda>
        #    return (lambda data: callback(*data), user_data)

        if file.get_uri_scheme() != 'file' or "Dropbox" in file.get_uri():
            return Nautilus.OperationResult.COMPLETE

        GObject.idle_add(self.update_emblem, provider, handle, closure, file)
        #file.invalidate_extension_info()
        return Nautilus.OperationResult.IN_PROGRESS
    
    def update_emblem(self, provider, handle, closure, file):
        for tag in self.tag_settings:
            if self.tracker.has_tag(file.get_uri(), tag):
                file.add_emblem(self.tag_settings[tag][0])
        file.invalidate_extension_info()
        Nautilus.info_provider_update_complete_invoke(closure, provider, handle, Nautilus.OperationResult.COMPLETE)
        return False
        #return Nautilus.OperationResult.COMPLETE


    def tag_file_cb(self, menu, file, tag):
        for f in file:
            for f_tag in self.tag_settings:
                if self.tracker.has_tag(f.get_uri(), f_tag):
                    self.tracker.remove_tag(f.get_uri(), f_tag)
            tag_added = self.tracker.add_tag(f.get_uri(), tag)
            if tag_added:
                f.add_emblem(self.tag_settings[tag][0])
                #f.invalidate_extension_info()
            
    def tag_file_remove_cb(self, menu, file):
        for f in file:
            for tag in self.tag_settings:
                if self.tracker.has_tag(f.get_uri(), tag):
                    self.tracker.remove_tag(f.get_uri(), tag)
            f.invalidate_extension_info()
        
    def get_file_items(self, window, files):
        # Show the menu if there is at least one file selected
        if len(files) == 0:
            return


        for fd in files:
            # Only for local files
            if fd.get_uri_scheme() != 'file':
                return
            # Not in the Archive
            if self.archive_folder.get_uri() in fd.get_uri():
                return
        
        items = []
        tags = [tag for tag in self.tag_settings]
        tags.sort()
        
        top_menuitem = Nautilus.MenuItem(
            name="ArchiveTagExtension::Menu",
            label="Archive Tags"
        )
        submenu = Nautilus.Menu()
        top_menuitem.set_submenu(submenu)
        
        for tag in tags:     
            set_tag = Nautilus.MenuItem(
                name="ArchiveTagExtension::Add_%s_Tag" % tag,
                label="Tag for %s" % tag.capitalize(),
            )
            set_tag.connect('activate', self.tag_file_cb, files, tag)
            submenu.append_item(set_tag)
        
        remove_tag = Nautilus.MenuItem(
            name="ArchiveTagExtension::Remove_Archive_Tag",
            label="Remove Archive Tags",
        )
        remove_tag.connect('activate', self.tag_file_remove_cb, files)
        
        submenu.append_item(remove_tag)
        
        return top_menuitem,


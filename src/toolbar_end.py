# Copyright (c) 2014-2016 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gio, GLib

from lollypop.pop_next import NextPopover
from lollypop.pop_queue import QueueWidget
from lollypop.pop_search import SearchPopover
from lollypop.define import Lp, Shuffle


class ToolbarEnd(Gtk.Bin):
    """
        Toolbar end
    """

    def __init__(self, app):
        """
            Init toolbar
            @param app as Gtk.Application
        """
        Gtk.Bin.__init__(self)
        self.connect('show', self._on_show)
        self.connect('hide', self._on_hide)
        self._pop_next = NextPopover()
        self._queue = None
        self._search = None
        self._timeout_id = None
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Lollypop/ToolbarEnd.ui')
        builder.connect_signals(self)

        self.add(builder.get_object('end'))

        self._grid_next = builder.get_object('grid-next')

        self._shuffle_button = builder.get_object('shuffle-button')
        self._shuffle_image = builder.get_object('shuffle-button-image')
        shuffleAction = Gio.SimpleAction.new('shuffle-button', None)
        shuffleAction.connect('activate', self._activate_shuffle_button)
        app.add_action(shuffleAction)
        app.set_accels_for_action("app.shuffle-button", ["<Control>r"])
        Lp().settings.connect('changed::shuffle', self._shuffle_button_aspect)

        self._party_button = builder.get_object('party-button')
        party_action = Gio.SimpleAction.new('party', None)
        party_action.connect('activate', self._activate_party_button)
        app.add_action(party_action)
        app.set_accels_for_action("app.party", ["<Control>p"])

        self._search_button = builder.get_object('search-button')
        searchAction = Gio.SimpleAction.new('search', None)
        searchAction.connect('activate', self._on_search_button_clicked)
        app.add_action(searchAction)
        app.set_accels_for_action("app.search", ["<Control>f"])

        self._queue_button = builder.get_object('queue-button')
        queueAction = Gio.SimpleAction.new('queue', None)
        queueAction.connect('activate', self._on_queue_button_clicked)
        app.add_action(queueAction)
        app.set_accels_for_action("app.queue", ["<Control>l"])

        self._settings_button = builder.get_object('settings-button')

        Lp().player.connect('party-changed', self._on_party_changed)
        Lp().player.connect('queue-changed', self._on_queue_changed)

    def setup_menu(self, menu):
        """
            Add an application menu to menu button
            @parma: menu as Gio.Menu
        """
        self._settings_button.show()
        self._settings_button.set_menu_model(menu)

    def on_status_changed(self, player):
        """
            Update buttons on status changed
            @param player as Player
        """
        if player.is_playing():
            # Party mode can be activated
            # via Fullscreen class, so check button state
            self._party_button.set_active(player.is_party())

    def on_next_changed(self, player, force=False):
        """
            Show next popover
            @param player as Player
            @param force to show the popover
        """
        self._timeout_id = None
        if not self.is_visible() or not self._pop_next.should_be_shown():
            if not force:
                self._pop_next.hide()
                return
        # Do not show next popover for non internal tracks as
        # tags will be readed on the fly
        if player.next_track.id is not None and\
           player.next_track.id >= 0 and\
            (player.is_party() or
             Lp().settings.get_enum('shuffle') == Shuffle.TRACKS):
            self._pop_next.update()
            if not self._pop_next.is_visible():
                self._pop_next.set_relative_to(self._grid_next)
                self._pop_next.show()
        else:
            self._pop_next.hide()

#######################
# PRIVATE             #
#######################
    def _on_button_press(self, button, event):
        """
            Show next popover on long press
            @param widget as Gtk.Widget
            @param event as Gdk.Event
        """
        self._timeout_id = GLib.timeout_add(500, self.on_next_changed,
                                            Lp().player, True)

    def _on_button_release(self, button, event):
        """
            If next popover shown, block event
            @param widget as Gtk.Widget
            @param event as Gdk.Event
        """
        if self._timeout_id is None:
            return True
        else:
            GLib.source_remove(self._timeout_id)
            self._timeout_id = None

    def _set_shuffle_icon(self):
        """
            Set shuffle icon
        """
        shuffle = Lp().settings.get_enum('shuffle')
        if shuffle == Shuffle.NONE:
            self._shuffle_image.get_style_context().remove_class(
                                                                    'selected')
            self._shuffle_image.set_from_icon_name(
                "media-playlist-consecutive-symbolic",
                Gtk.IconSize.SMALL_TOOLBAR)
        else:
            self._shuffle_image.set_from_icon_name(
                "media-playlist-shuffle-symbolic",
                Gtk.IconSize.SMALL_TOOLBAR)
            if shuffle == Shuffle.TRACKS:
                self._shuffle_image.get_style_context().add_class(
                                                                    'selected')
            else:
                self._shuffle_image.get_style_context().remove_class(
                                                                    'selected')
        self.on_next_changed(Lp().player)

    def _shuffle_button_aspect(self, settings, value):
        """
            Mark shuffle button as active when shuffle active
            @param settings as Gio.Settings, value as str
        """
        self._set_shuffle_icon()

    def _activate_party_button(self, action=None, param=None):
        """
            Activate party button
            @param action as Gio.SimpleAction
            @param param as GLib.Variant
        """
        self._party_button.set_active(not self._party_button.get_active())
        Lp().window.responsive_design()

    def _activate_shuffle_button(self, action=None, param=None):
        """
            Activate shuffle button
            @param action as Gio.SimpleAction
            @param param as GLib.Variant
        """
        self._shuffle_button.set_active(not self._shuffle_button.get_active())

    def _on_search_button_clicked(self, obj, param=None):
        """
            Show search widget on search button clicked
            @param obj as Gtk.Button or Gtk.Action
        """
        if self._search is None:
            self._search = SearchPopover(self)
        self._search.set_relative_to(self._search_button)
        self._search.show()

    def _on_queue_button_clicked(self, button, param=None):
        """
            Show queue widget on queue button clicked
            @param obj as Gtk.Button or Gtk.Action
        """
        if self._queue is None:
            self._queue = QueueWidget()
        self._queue.set_relative_to(self._queue_button)
        self._queue.show()

    def _on_party_button_toggled(self, button):
        """
            Set party mode on if party button active
            @param obj as Gtk.button
        """
        active = self._party_button.get_active()
        self._shuffle_button.set_sensitive(not active)
        if not Lp().settings.get_value('dark-ui'):
            settings = Gtk.Settings.get_default()
            settings.set_property("gtk-application-prefer-dark-theme", active)
        Lp().player.set_party(active)
        self.on_next_changed(Lp().player)

    def _on_queue_changed(self, player):
        """
            On queue changed, change buttno aspect
            @param player as Player
            @param is party as bool
        """
        if player.get_queue():
            self._queue_button.get_style_context().add_class('selected')
        else:
            self._queue_button.get_style_context().remove_class('selected')

    def _on_party_changed(self, player, is_party):
        """
            On party change, sync toolbar
            @param player as Player
            @param is party as bool
        """
        if self._party_button.get_active() != is_party:
            self._activate_party_button()

    def _on_show(self, widget):
        """
            Show popover if needed
            @param widget as Gtk.Widget
        """
        self._set_shuffle_icon()

    def _on_hide(self, widget):
        """
            Hide popover
            @param widget as Gtk.Widget
        """
        self._pop_next.hide()

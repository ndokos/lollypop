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

from threading import Thread

from lollypop.charts_itunes import ItunesCharts
from lollypop.charts_spotify import SpotifyCharts


class Charts:
    """
        Charts
    """

    def __init__(self):
        """
            Init charts
        """
        self.__providers = [SpotifyCharts(), ItunesCharts()]

    def update(self):
        """
            Update charts
        """
        t = Thread(target=self.__update)
        t.daemon = True
        t.start()

    def stop(self):
        """
            Stop downloads
        """
        for provider in self.__providers:
            provider.stop()

#######################
# PRIVATE             #
#######################
    def __update(self):
        """
            Update charts
            @thread safe
        """
        for provider in self.__providers:
            provider.update()

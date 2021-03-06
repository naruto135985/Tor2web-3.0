"""
    Tor2web
    Copyright (C) 2012 Hermes No Profit Association - GlobaLeaks Project

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""

:mod:`Tor2Web`
=====================================================

.. automodule:: Tor2Web
   :synopsis: [GLOBALEAKS_MODULE_DESCRIPTION]

.. moduleauthor:: Arturo Filasto' <art@globaleaks.org>
.. moduleauthor:: Giovanni Pellerano <evilaliv3@globaleaks.org>

"""

# -*- coding: utf-8 -*-

VERSION = "Tor2Web 3.0 Beta 1"

import os
import re
import ConfigParser
from storage import Storage

listpattern = re.compile(r'\s*("[^"]*"|.*?)\s*,')

class Config(Storage):
    """
    A Storage-like class which loads and store each attribute into a portable
    conf file.
    """
    def __init__(self, cfgfile="/etc/tor2web.conf"):
        Storage.__init__(self)
        self._file = cfgfile
        self._section = 'main'
        self._parser = ConfigParser.ConfigParser()

    def load(self):
        try:
            if (not os.path.exists(self._file) or
                not os.path.isfile(self._file) or
                not os.access(self._file, os.R_OK)):
                print "Tor2web Startup Failure: cannot open config file (%s)" % self._file
                exit(1)
        except:
            print "Tor2web Startup Failure: error while accessing config file (%s)" % self._file
            exit(1)

        try:
            self._parser.read([self._file])

            for name in self._parser.options(self._section):
                value = self._parser.get(self._section, name)
                self.__dict__[name] = self.parse(name)
        except:
            raise Exception("Tor2web Error: invalid config file (%s)" % self._file)

    def store(self):
        """
        Commit changes in config file.
        """
        if self._file is None:
            raise Exception("Tor2web Error: cannot store configuration (never loaded)")

        self._file = open(self._file, 'w')
        try:
            self._parser.write(self._file)
        finally:
            self._file.close()

    def splitlist(self, line):
        return [x[1:-1] if x[:1] == x[-1:] == '"' else x
            for x in listpattern.findall(line.rstrip(',') + ',')]

    def parse(self, name):
        try:

           value = self._parser.get(self._section, name)
           if value.isdigit():
                value = int(value)
           elif value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
           elif value.lower() in ('', 'none'):
                value = None
           elif value[0] == "[" and value[-1] == "]":
                value = self.splitlist(value[1:-1])

           return value

        except ConfigParser.NoOptionError:
            # if option doesn't exists returns None
            return None

    def __getattr__(self, name):
        return self.__dict__.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

        # keep an open port with private attributes
        if name.startswith("_"):
            return

        try:

            # XXX: Automagically discover variable type
            self._parser.set(self._section, name, value)

        except ConfigParser.NoOptionError:
            raise NameError(name)

config = Config()

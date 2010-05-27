"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2007  Nathanael C. Fritz
    This file is part of SleekXMPP.

    SleekXMPP is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    SleekXMPP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with SleekXMPP; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import logging
from wannabe import Wannabe
from . import __all__

class base_plugin(object):

    def __init__(self, xmpp, config):
        self.xep = 'base'
        self.description = 'Base Plugin'
        self.xmpp = xmpp
        self.config = config
        self.enable = config.get('enable', True)
        if self.enable:
            self.plugin_init()

    def plugin_init(self):
        pass

    def plugin_shut_down(self):
        pass

    def post_init(self):
        pass


class PluginDict(dict):
    """A dictionary class for plugins"""

    def __init__(self, xmpp):
        super(PluginDict, self).__init__()
        self.xmpp = xmpp

    def __getitem__(self, key):
        """If the key is not present, add and return a Wannabe object
        to serve as a placeholder for calls."""

        if key in self.keys():
            return super(PluginDict, self).__getitem__(key)
        else:
            logging.debug("Plugin not in dict %s yet." % key)
            value = Wannabe()
            super(PluginDict, self).__setitem__(key, value)
            return value


    def __setitem__(self, key, value):
        """If the current item with key is a Wannabe, execute pending
        calls for value and put it in the dictionary."""

        if key in self.keys():
            current = super(PluginDict, self).__getitem__(key)
            if isinstance(current, Wannabe):
                current._Wanabe_become(value)

        return super(PluginDict, self).__setitem__(key, value)


    def __delitem__(self, key):
        """Calls plugin_shut_down and then remove it form the dictionary"""

        if key in self.keys():
            current = super(PluginDict, self).__getitem__(key)
            if isinstance(current, base_plugin):
                current.plugin_shut_down()

        super(PluginDict, self).__delitem__(key)


    def register_plugin(self, name, config = {}):
        """Register a plugin from the same directory of this file."""
        if name in self.keys():
            return
        module = __import__("%s.%s" % (globals()['__package__'], name), fromlist = name)
        self[name] = getattr(module, name)(self.xmpp, config)
        xep = "(XEP-%s) " % getattr(self[name], 'xep', '')
        logging.debug("Loaded Plugin %s%s" % (xep, self[name].description))


    def register_plugins(self, include = '__all__', exclude = set(), config = dict()):
        """Register multiple plugins

        include -- set of plugins names to register or
                   if empty uses plugins/__init__.__all__
        exclude -- set of plugins names to ignored. (default = empty set)
        config  -- dict plugin_name:config. (default = empty dict)
        """

        if not include:
            include = __all__

        for plugin in set(include).difference(set(exclude)):
            self.register_plugin(plugin, config.get(plugin, {}))


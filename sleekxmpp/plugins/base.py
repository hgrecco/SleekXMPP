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
    
    def post_init(self):
        pass



class PluginDict(dict):
    """A dictionary class for plugins"""

    def __getitem__(self, key):
        """If the key is not present, add and return a CallRecorder object
        to serve as a placeholder for calls."""
        
        if key in self.keys():
            return super(PluginDict, self).__getitem__(key)        
        else:
            logging.debug("Plugin not in dict %s yet." % key)                                    
            value = CallRecorder()
            super(PluginDict, self).__setitem__(key, value)
            return value

    def __setitem__(self, key, value):
        """If the current item with key is a CallRecorder, execute pending 
        calls for value and put it in the dictionary."""
        
        if key in self.keys():
            current = super(PluginDict, self).__getitem__(key)
            if isinstance(current, CallRecorder):                
                for c, h in current.calls:
                    logging.debug("Pending calls for %s -> %s" % (key, c))                                    
                    getattr(value, c)(*h.args, **h.kwargs)    
        
        return super(PluginDict, self).__setitem__(key, value)


class CallRecorder(object):
    """An object to be used as a placeholder for future calls on other objects."""
    
    def __init__(self):
        self.calls = list()        

    def __getattr__(self, name):         
        h = HungryObject()
        self.calls.append((name, h))
        return h
        
class HungryObject(object):
    """An object to keep track of calling arguments."""    
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
            

if __name__ == '__main__':
    current = CallRecorder()
    current.__add__(3)
    value = 1
    for c, h in current.calls:
        print getattr(value, c)(*h.args, **h.kwargs)    

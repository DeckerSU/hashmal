from pkg_resources import iter_entry_points
import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from dock_handler import DockHandler

required_plugins = ['Stack Evaluator', 'Variables']
"""These plugins are needed and cannot be disabled."""

class PluginHandler(QWidget):
    """Handles loading/unloading plugins."""
    def __init__(self, main_window):
        super(PluginHandler, self).__init__(main_window)
        self.gui = main_window
        self.config = main_window.config
        self.loaded_plugins = []
        self.dock_handler = None
        self.config.optionChanged.connect(self.on_option_changed)

    def get_plugin(self, plugin_name):
        for plugin in self.loaded_plugins:
            if plugin.name == plugin_name:
                return plugin
        return None

    def load_plugins(self):
        """Load plugins from entry points."""
        for entry_point in iter_entry_points(group='hashmal.plugin'):
            plugin_maker = entry_point.load()
            plugin_instance = plugin_maker()
            plugin_instance.name = entry_point.name

            self.loaded_plugins.append(plugin_instance)

        for req in required_plugins:
            if req not in [i.name for i in self.loaded_plugins]:
                print('Required plugin "{}" not found.\nTry running setup.py.'.format(req))
                sys.exit(1)

    def setup_docks(self):
        """Enable or disable plugin docks according to config file."""
        disabled_plugins = self.config.get_option('disabled_plugins', [])
        for plugin in self.loaded_plugins:
            is_enabled = plugin.name not in disabled_plugins
            self.dock_handler.set_dock_enabled(plugin.dock.tool_name, is_enabled)

    def create_dock_handler(self):
        """Create and return the Dock Handler."""
        self.dock_handler = DockHandler(self.gui, self)
        self.dock_handler.create_docks()
        self.setup_docks()

        return self.dock_handler

    def set_plugin_enabled(self, plugin_name, is_enabled):
        """Enable or disable a plugin and all its docks."""
        plugin = self.get_plugin(plugin_name)
        if plugin is None:
            return

        # Do not disable required plugins.
        if not is_enabled and plugin_name in required_plugins:
            return

        self.dock_handler.set_dock_enabled(plugin.tool_name, is_enabled)

    def on_option_changed(self, key):
        if key == 'disabled_plugins':
            self.setup_docks()

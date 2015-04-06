"""
    ahotkey.py
    author: Marcus Albertsson

    Small utility for setting up hotkey sets and easily switch between them
    during a maya session.
"""
import os
import logging
import ConfigParser

import pymel.core as pymel

logging.basicConfig(level=logging.DEBUG)
CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))


class HotkeyMenu(object):

    ARUDO_MENU_NAME = 'arudoMenu'
    HOTKEY_MENU_NAME = 'arudoHotkeyMenu'

    def __init__(self):
        self.mayaMenu()

    def mayaMenu(self):
        if not pymel.menu(self.ARUDO_MENU_NAME, exists=True):
            pymel.menu(
                self.ARUDO_MENU_NAME,
                label='Arudo',
                parent=pymel.melGlobals['gMainWindow'],
            )

        if pymel.menu(self.HOTKEY_MENU_NAME, exists=True):
            pymel.deleteUI(self.HOTKEY_MENU_NAME)

        pymel.menuItem(
            self.HOTKEY_MENU_NAME,
            label='Hotkey Set',
            subMenu=True,
            parent=self.ARUDO_MENU_NAME,
        )
        pymel.menuItem(
            label='maya default',
            command=lambda x: factory_hotkeys(),
            parent=self.HOTKEY_MENU_NAME,
        )

    def add_menu_hotkey_sets(self, section_name, hotkey_set):
        pymel.menuItem(
            label=section_name,
            command=lambda x: map_hotkeys(hotkey_set),
            parent=self.HOTKEY_MENU_NAME,
        )


class HotkeyParser(object):

    CONFIG_FILE = os.path.join(CURRENT_FILE_PATH, 'hotkeys.cfg')

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.CONFIG_FILE)
        self.hotkey_maps = {}
        self.option_map()

    def section_map(self, section):
        hotkey_dict = {}
        options = self.config.options(section)
        for option in options:
            hotkey_dict[option] = self.config.get(section, option).split(',')

        return hotkey_dict

    def option_map(self):
        sections = self.config.sections()
        for section in sections:
            self.hotkey_maps[section] = self.section_map(section)

    def update(self):
        self.option_map()

    def get_hotkeys(self):
        return self.hotkey_maps

    def get_section(self, section):
        return self.hotkey_maps[section]


class HotkeyMapper(object):

    SCRIPT_TYPE = 'python'

    def __init__(self, hotkey_commands, category=None):
        self.category = category or 'arudo'
        self.command_key_map = hotkey_commands
        self.hotkey_kwargs = {}

    def perform_map_hotkeys(self):
        for hotkey, name_command in self.command_key_map.iteritems():

            log_msg = '{0: <14} :: {1}'.format(hotkey, ':'.join(name_command))
            logging.debug(log_msg)

            self.hotkey = hotkey
            self.name, self.command = name_command
            self.string_command = self.get_func_string_call()

            if not pymel.runTimeCommand(self.name, q=True, exists=True):
                self.create_runtime_command()

            self.create_name_command()
            self.set_hotkeys()

    def get_func_string_call(self):
        module = self.command.split('.')[0]
        return 'import {0}; {1}'.format(module, self.command)

    def create_runtime_command(self):
        runTime_kwargs = {
            'annotation': self.name,
            'command': self.string_command,
            'category': self.category,
            'commandLanguage': self.SCRIPT_TYPE,
            'default': True,
        }
        pymel.runTimeCommand(self.name, **runTime_kwargs)

    def create_name_command(self):
        pymel.nameCommand(
            self.name,
            ann=self.name,
            c=self.name,
            default=True,
            sourceType=self.SCRIPT_TYPE,
        )

    def set_hotkeys(self):
        hotkey = self.hotkey
        hotkey_kwargs = {}

        if 'alt' in hotkey:
            hotkey = hotkey.replace('alt+', '')
            hotkey_kwargs['alt'] = True
        if 'ctrl' in hotkey:
            hotkey = hotkey.replace('ctrl+', '')
            hotkey_kwargs['ctl'] = True

        hotkey_kwargs['name'] = self.name
        pymel.hotkey(k=hotkey, **hotkey_kwargs)


def map_hotkeys(hotkey_section, category='arudo'):
    factory_hotkeys()
    HotkeyMapper(hotkey_section, category).perform_map_hotkeys()


def factory_hotkeys():
    pymel.hotkey(factorySettings=True)


def setup_arudo_hotkeys():
    hotkey_cfg = HotkeyParser()
    hotkey_cfg.update()
    hotkey_maps = hotkey_cfg.get_hotkeys()

    hotkey_menu = HotkeyMenu()
    for each in hotkey_maps.keys():
        hotkey_menu.add_menu_hotkey_sets(each, hotkey_maps[each])

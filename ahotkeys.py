"""
    ahotkeys.py
    author: Marcus Albertsson

    Small hotkey utility.
"""
import logging
import functools

import pymel.core as pymel
from hotkeys import HOTKEYS

logging.basicConfig(level=logging.DEBUG)


class Hotkey(object):

    CATEGORY = 'arudo'
    SCRIPT_TYPE = 'python'

    def __init__(self, hotkey_commands):
        self.command_key_map = hotkey_commands
        self.hotkey_kwargs = {}

        # init ui
        self.initUI()

    def initUI(self):
        if not pymel.menu('arudoMenu', exists=True):
            arudo_menu = pymel.menu('arudoMenu',
                label='Arudo', parent=pymel.melGlobals['gMainWindow'])

        if pymel.menu('arudoHotkeyMenu', exists=True):
            pymel.deleteUI('arudoHotkeyMenu')

        hotkey_menu = pymel.menuItem('arudoHotkeyMenu',
            label='Hotkey Set', subMenu=True, parent='arudoMenu')

        pymel.menuItem(label='maya default', command=lambda x: factory_hotkeys(),
            parent=hotkey_menu)
        pymel.menuItem(label='arudo', command=lambda x: map_hotkeys(), parent=hotkey_menu)

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
            'category': self.CATEGORY,
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


def map_hotkeys():
    Hotkey(HOTKEYS).perform_map_hotkeys()

def factory_hotkeys():
    pymel.hotkey(factorySettings=True)


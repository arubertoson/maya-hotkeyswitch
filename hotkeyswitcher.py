"""
"""
import os
import re
import json
import string

import maya.cmds as cmds

# Regular expression for comments
comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
    )

# Menu Constants
MENU_NAME = 'arudo_menu'
HOTKEY_CATEGORY = 'arudo'
SCRIPT_TYPE = 'python'

OPTVAR = 'mhotkeyswitcher_crnt_set'

# Paths
CWD = None
CONFIG_PATHS = None


def parse_json(filename):
    """ Strips comments from given file returning a json object. """
    with open(str(filename)) as f:
        content = ''.join(f.readlines())

        # Looking for comments
        match = comment_re.search(content)
        while match:
            # single line comment
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)

        return json.loads(content)


def get_hotkey_files(paths=CONFIG_PATHS):
    hfiles = {}
    for p in paths:
        if not p.exists():
            continue
        for f in p.files():
            if not f.ext == '.hotkey':
                continue
            hfiles[f.namebase] = f
    return hfiles


def cmd_exists(name):
    return cmds.runTimeCommand(name, q=True, exists=True)


def run():
    if HotkeySwitch.instance is None:
        HotkeySwitch.instance = HotkeySwitch()

        create_ui()


class Hotkey(object):
    """
    A class holding the necessary information for creating a hotkey in
    maya.
    """

    def __init__(self, name, key, cmd):
        self.name = name
        self.key = list(key)
        self.key_args = self.parse_hotkey(key)
        self.cmd = self.parse_cmd(cmd)

    def parse_cmd(self, cmd):
        """Pars command string for maya hotkey."""
        module = cmd.split('.')[0]
        return 'import {0}; {1}'.format(module, cmd)

    def parse_hotkey(self, key):
        """Parse keyboard input string for maya hotkey."""
        kwargs, key_list = {}, key
        kwargs['name'] = self.name

        if 'alt' in key_list:
            kwargs['alt'] = True
            key_list.remove('alt')

        if 'ctrl' in key_list:
            kwargs['ctl'] = True
            key_list.remove('ctrl')

        kwargs['k'] = key_list.pop()
        return kwargs


class HotkeySwitch(object):
    """
    Main hotkey switcher class.

    Manages existing hotkey bindings and able to switch between them.
    """
    instance = None

    def __init__(self, category=None, script_type=None):
        self.active = ''
        self.hotkey_map = {}
        self.category = category or HOTKEY_CATEGORY
        self.script_type = script_type or SCRIPT_TYPE
        self.hotkey_files = get_hotkey_files()

    def __getitem__(self, key):
        return self.HOTKEY_MAP[key]

    def __iter__(self):
        return iter(self.HOTKEY_MAP)

    def create_runtime_cmd(self, key):
        cmds.runTimeCommand(
            key.name,
            annotation=key.name,
            command=key.cmd,
            category=self.category,
            commandLanguage=self.script_type,
            default=True,
        )

    def create_name_cmd(self, key):
        cmds.nameCommand(
            key.name,
            ann=key.name,
            c=key.name,
            default=True,
            sourceType=self.script_type,
        )

    def parse_hotkeys(self):
        """Parse existing hotkey files and create hotkey map."""
        for name, f in self.hotkey_files.iteritems():
            json_data = self.parse_json(f)
            self.hotkey_map[name] = [Hotkey(**key_map)
                                     for key_map in json_data]

    def set_factory(self):
        self.active = ''
        cmds.hotkey(factorySettings=True)

    def update(self):
        self.hotkey_map = {}
        self.hotkey_files = get_hotkey_files()
        self.


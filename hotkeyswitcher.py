"""
This script makes it easier to keep track of hotkeys between maya versions,
also making it possible to edit outside of maya and without the (in my
opinion) terrible hotkey interface.

No need to hunt down named commands and hotkeyfiles when going up and down
in Maya versions.

Put the script inside a valid PYTHONPATH directory and fire the below in
maya.

Usage::

    >>> import hotkeyswitcher
    >>> hotkeyswitcher.run()
"""
import os
import re
import json
from functools import partial

import maya.cmds as cmds
import maya.mel as mel


__title__ = 'hotkeyswitcher'
__version__ = '0.1'
__author__ = 'Marcus Albertsson'
__email__ = 'marcus.arubertoson@gmail.com'
__url__ = 'http://github.com/arubertoson/maya-hotkeyswitcher'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Marcus Albertsson'


# Menu Constants
MENU_NAME = 'arudo_menu'
HOTKEY_MENU_NAME = 'arudoHotkeyMenu'
HOTKEY_CATEGORY = 'arudo'
SCRIPT_TYPE = 'python'
OPTVAR = 'mhotkeyswitcher_crnt_set'


# Paths
CWD = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATHS = [CWD]


# Regular expression for comments in json files
comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
    )


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
    """Collect hotkey config files from given config paths."""
    hfiles = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        for f in os.listdir(p):
            if not f.endswith('.hotkey'):
                continue
            hfiles[os.path.splitext(f)[0]] = os.path.join(p, f)
    return hfiles


def cmd_exists(name):
    return cmds.runTimeCommand(name, q=True, exists=True)


class Hotkey(object):
    """
    A class holding the necessary information for creating a hotkey in
    maya.
    """

    def __init__(self, filename, name, key, cmd):
        self.name = '{}_{}'.format(filename, name)
        self.key = list(key)
        self.key_args = self.parse_hotkey(key)
        self.cmd = self.parse_cmd(cmd)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)

    def parse_cmd(self, cmd):
        """Pars command string for maya hotkey."""
        if 'import' in cmd:
            return cmd
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
        self.parse_hotkeys()

    def __repr__(self):
        return 'HotkeySwitch({})'.format(list(self.hotkey_map))

    def __getitem__(self, key):
        return self.hotkey_map[key]

    def __iter__(self):
        return iter(self.hotkey_map)

    def _add_menu_items(self):
        for item in self.hotkey_map:
            cmds.menuItem(l=item.title(), c=partial(self.set_hotkeys, item))
            cmds.menuItem(ob=True, c=partial(self.edit, item))

    def initUI(self):
        """Creates the interface."""
        if not cmds.menu(MENU_NAME, exists=True):
            cmds.menu(
                MENU_NAME,
                label='Arudo',
                parent=mel.eval('$htkeyswitch = $gMainWindow'),
            )

        if cmds.menu(HOTKEY_MENU_NAME, exists=True):
            cmds.deleteUI(HOTKEY_MENU_NAME, menuItem=True)

        cmds.menuItem(
            HOTKEY_MENU_NAME,
            label='Hotkey Set',
            subMenu=True,
            allowOptionBoxes=True,
            insertAfter='',
            parent=MENU_NAME,
            )
        cmds.menuItem(l='Maya Default', c=lambda *args: self.set_factory())
        cmds.menuItem(divider=True)
        self._add_menu_items()
        cmds.menuItem(divider=True)
        cmds.menuItem(l='Update', c=lambda *args: self.update())
        cmds.menuItem(l='Print Current', c=lambda *args: self.output())

    def edit(self, key_map, *args):
        """Open file in default text editor."""
        os.system('{0}'.format(self.hotkey_files[key_map]))

    def create_runtime_cmd(self, key):
        cmds.runTimeCommand(
            key.name,
            annotation=key.name,
            command=key.cmd,
            category=self.category,
            commandLanguage=self.script_type,
            # default=True,
        )

    def create_name_cmd(self, key):
        cmds.nameCommand(
            key.name,
            ann=key.name,
            c=key.name,
            # default=True,
            sourceType=self.script_type,
        )

    def parse_hotkeys(self):
        """Parse existing hotkey files and create hotkey map."""
        for name, f in self.hotkey_files.iteritems():
            json_data = parse_json(f)
            self.hotkey_map[name] = [Hotkey(name, **key_map)
                                     for key_map in json_data]

    def set_factory(self):
        """Set hotkeys back to Maya factory."""
        self.active = ''
        cmds.hotkey(factorySettings=True)

    def set_hotkeys(self, key_set, category=HOTKEY_CATEGORY, *args):
        """Set hotkeys to given key set under given category."""
        self.active = key_set
        cmds.optionVar(sv=(OPTVAR, key_set))
        for key in self.hotkey_map[key_set]:
            if not cmd_exists(key.name):
                self.create_runtime_cmd(key)
            self.create_name_cmd(key)
            cmds.hotkey(**key.key_args)

    def update(self):
        """
        Update hotkeymaps.

        Will find new hotkey setting files, or update current ones with
        changes.
        """
        self.clean_hotkeys()
        self.hotkey_files = get_hotkey_files()
        self.parse_hotkeys()
        if self.active:
            cmds.hotkey(factorySettings=True)
            self.set_hotkeys(self.active)
        self.initUI()

    def clean_hotkeys(self):
        """
        Removes existing hotkey runTimeCommands and empties hotkey map
        dictionary.
        """
        for m, hotkeys in self.hotkey_map.iteritems():
            for i in hotkeys:
                if cmd_exists(i.name):
                    cmds.runTimeCommand(i.name, e=True, delete=True)
        self.hotkey_map = {}

    def output(self):
        """
        Outputs current hotkey bindings to script editor in readable format.
        """
        if not self.active:
            print('Maya Default')
            return
        for key in self.hotkey_map[self.active]:
            name = '{0: >32}'.format(key.name)
            key_stroke = '{0: >18}'.format('+'.join(key.key))
            print('{0} :: {1} :: {2}'.format(name, key_stroke, key.cmd))


def init(clean_prefs=True):
    """
    Used to start hotkeyswitcher
    """
    if HotkeySwitch.instance is None:
        HotkeySwitch.instance = HotkeySwitch()

    if not cmds.optionVar(exists=OPTVAR):
        cmds.optionVar(sv=(OPTVAR, ''))

    if cmds.optionVar(q=OPTVAR):
        HotkeySwitch.instance.set_hotkeys(cmds.optionVar(q=OPTVAR))

    HotkeySwitch.instance.initUI()

    # Don't know if this will ever be wanted.
    # if clean_prefs:
        # cmds.scriptJob(event=['quitApplication', remove_hotkey_commands])


if __name__ == '__main__':
    init()

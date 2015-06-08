#! python
import os
import json

from json_minify import json_minify

import pymel.core as pymel
import pymel.util.path as Path
from pymel.core.language import optionVar

STARTUP_KEY_SET = 'model'
ahotkey_optionvar = 'ahotkey_current_key_set'
CWD = Path(__file__).dirname().expand()
CONFIG_PATHS = [CWD, Path(CWD.parent).joinpath('config')]


if ahotkey_optionvar not in optionVar:
    optionVar[ahotkey_optionvar] = STARTUP_KEY_SET


class Hotkey(object):

    def __init__(self, name, key, cmd):
        self.name = name
        self.key = list(key)
        self.key_args = self.__get_key_kwargs(key)
        self.cmd = self.__get_string_cmd(cmd)

    def __get_string_cmd(self, cmd):
        module = cmd.split('.')[0]
        return 'import {0}; {1}'.format(module, cmd)

    def __get_key_kwargs(self, key):
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


class MayaHotkey(object):

    MAP = {}
    ACTIVE = ''
    ARUDO_MENU_NAME = 'arudoMenu'
    HOTKEY_MENU_NAME = 'arudoHotkeyMenu'

    def __init__(self, category=None, script_type=None):
        self.category = category or 'arudo'
        self.script_type = script_type or 'python'
        self.update()
        self._initUI()
        self.map(optionVar[ahotkey_optionvar])

    def __getitem__(self, key):
        return self.MAP[key]

    def __iter__(self):
        return iter(self.MAP)

    def _add_menu_items(self):
        for item in self:
            pymel.menuItem(l=item.title(), c=lambda x: self.map(item))
            pymel.menuItem(ob=True, c=lambda x: self.edit(item))

    def _initUI(self):
        if not pymel.menu(self.ARUDO_MENU_NAME, exists=True):
            pymel.menu(
                self.ARUDO_MENU_NAME,
                label='Arudo',
                parent=pymel.melGlobals['gMainWindow'],
            )

        if pymel.menu(self.HOTKEY_MENU_NAME, exists=True):
            pymel.deleteUI(self.HOTKEY_MENU_NAME, menuItem=True)

        with pymel.menuItem(
            self.HOTKEY_MENU_NAME,
            label='Hotkey Set',
            subMenu=True,
            allowOptionBoxes=True,
            parent=self.ARUDO_MENU_NAME,
        ):
            pymel.menuItem(l='Maya Default', c=lambda x: self.factory())
            pymel.menuItem(divider=True)
            self._add_menu_items()
            pymel.menuItem(divider=True)
            pymel.menuItem(l='Update', c=lambda x: self.update())
            pymel.menuItem(l='Print Current', c=lambda x: self.output())

    def _get_json_string(self, hfile):
        with open(str(hfile), 'r') as f:
            json_string = json_minify(''.join(f.readlines()))
            json_data = json.loads(json_string)
        return json_data

    def _get_hfiles(self):
        hfiles = {}
        for p in CONFIG_PATHS:
            if not p.exists():
                continue
            for f in p.files():
                if not f.ext == '.hotkey':
                    continue
                hfiles[f.namebase] = f
        return hfiles

    def _parse(self):
        self.MAP = {}
        for name, f in self.hfiles.iteritems():
            json_data = self._get_json_string(f)
            self.MAP[name] = [Hotkey(**key_map) for key_map in json_data]

    def _runtime_command(self, key):
        pymel.runTimeCommand(
            key.name,
            annotation=key.name,
            command=key.cmd,
            category=self.category,
            commandLanguage=self.script_type,
            default=True,
        )

    def _name_command(self, key):
        pymel.nameCommand(
            key.name,
            ann=key.name,
            c=key.name,
            default=True,
            sourceType=self.script_type,
        )

    def cmd_exists(self, name):
        return pymel.runTimeCommand(name, q=True, exists=True)

    def output(self):
        if not self.ACTIVE:
            print('Maya Default')
            return
        for key in self[self.ACTIVE]:
            name = '{0: >24}'.format(key.name)
            key_stroke = '{0: >18}'.format('+'.join(key.key))
            print('{0} :: {1} :: {2}'.format(name, key_stroke, key.cmd))

    def edit(self, key_map):
        os.system('{0}'.format(self.hfiles[key_map]))

    def update(self):
        self.hfiles = self._get_hfiles()
        self._parse()
        self._initUI()

    def factory(self):
        self.ACTIVE = optionVar[ahotkey_optionvar] = ''
        pymel.hotkey(factorySettings=True)

    def map(self, key_set, category='arudo'):
        self.ACTIVE = optionVar[ahotkey_optionvar] = key_set
        for key in self[key_set]:

            if not self.cmd_exists(key.name):
                self._runtime_command(key)

            self._name_command(key)
            pymel.hotkey(**key.key_args)

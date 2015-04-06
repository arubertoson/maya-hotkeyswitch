import os
import json
import ConfigParser
import importlib
from pprint import pprint

import hotkeys

print dir(hotkeys)

for t in dir(hotkeys):
    if t.startswith('__'):
        continue

    test = hotkeys.__dict__[t]

pprint(test)

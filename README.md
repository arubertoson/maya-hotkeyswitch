As of now this repo is a bit redundant, everything works fine and if you want to use the
hotkeyswitcher without utilizing other preference options the by all means go ahead.

More functionality can be found in maya-mamprefs.

Hotkey utility for Autodesk Maya
================================

I grew tired of constantly having to keep track of my named commands file
together with my hotkey file. This was especially cumbersome when switching
around between versions, workplaces and having coworkers not wanting to
touch my computer when showing stuff due to excessive use of hotkeys.

The result was: *hotkeyswitcher*.

Now the hotkey setting file is away from the normal preferences and easily
customizable both during Maya sessions and outside of them and it's easy to
have different hotkey sets depending on the task you are performing
(animation, modeling etc.).


Features
========

* Easy and Manageable hotkeys
* Switching between different hotkey sets

Installation
============

Put the **hotkeyswitcher.py** in a valid Maya PYTHONPATH directory.
Preferably with your *.hotkey* files in the same directory. If you want
them in another directory you must specify the full path and add it
to the list variable in the script called *CONFIG_PATHS*:

    >>> CWD = os.path.abspath(os.path.dirname(__file__))
    >>> CONFIG_PATHS = [CWD, 'C:\Users\Macke\Documents\']


Usage
-----

The *.hotkey* files utilizes the json format together with comments. The format
used to create a hotkey is made with readability in mind and it's written
to encourage functions collected in scripts instead of having functions hidden
away in a Maya named commands.

    {
        // This is a comment
        {"name": "mask_vertex", "key": ["ctrl", "alt", "c"], "cmd": "import testy; testy.run()"},
        {"name": "mask_vertex", "key": ["alt", "C"], "cmd": "testy.run()"}
    }

The key list `["ctrl", "alt", "c"]` represents the key combination. Where
`["alt", "C"]` also includes a shift modifier. It also supports both
`cmd` formats above. an explicit `import` will always take priority. But when
there is no `import` as in: `testy.run()` the script assumes that *testy* is
the module and *run()* is the function meaning it imports the module
automatically.


Limitations
===========

Release hotkeys not yet implemented. Will implement when the need arises.

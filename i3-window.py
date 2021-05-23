#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from i3ipc import Connection, Event

parser = ArgumentParser(
    description="Prints the title of the currently focused i3 window for given monitor."
)

parser.add_argument(
    "monitor",
    type=str,
    help="The monitor name according to xrandr",
    nargs="+",
    default=None,
)

argsv = parser.parse_args()
i3 = Connection()
monitor = argsv.monitor[0]
output = i3.get_tree().find_named(f"^{monitor}$")

if not output:  # monitor not found
    print("Cannot find specified monitor.")
    sys.exit()
else:
    output = output[0]  # id

def print_window_title(t):
    print(t, flush=True)

def print_focused_window_title():
    tree = i3.get_tree()
    focused = tree.find_focused()
    print_window_title(focused.name)

def on_window(i3, e):
    d = e.ipc_data
    while 'output' not in d:
        d = d['container']
        if not d: return
    if d['output'] == monitor:
        print_window_title(d['name'])

def on_window_close(i3, e):
    d = e.ipc_data
    while 'output' not in d:
        d = d['container']
        if not d: return
    if d['output'] == monitor:
        print_focused_window_title()

def on_workspace(i3, e):
    if e.current.ipc_data["output"] == monitor:
        print_focused_window_title()

i3.on(Event.WINDOW_FOCUS, on_window)
i3.on(Event.WINDOW_TITLE, on_window)
i3.on(Event.WINDOW_NEW, on_window)
i3.on(Event.WINDOW_MOVE, on_window)
i3.on(Event.WINDOW_CLOSE, on_window_close)
i3.on(Event.WORKSPACE_FOCUS, on_workspace)

try:
    i3.main()
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

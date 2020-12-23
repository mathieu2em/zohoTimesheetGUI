import PySimpleGUI as sg
import sys  # For simplicity, we'll read config file from 1st CLI param sys.argv[1]
import json
import logging
import subprocess

import requests
import time
import webbrowser

sg.theme('DarkAmber')   # Add a touch of color



def main():
    global config
    config = json.load(open("credentials.json"))

    # ----------- Create the 3 layouts this Window will display -----------
    layout1 = [[sg.Text('First, you have to get a token from zoho')],
                [sg.Button('Ok'), sg.Button('Exit')]]

    layout2 = [[sg.Text('This is layout 2')]]

    # ----------- Create actual layout using Columns and a row of Buttons
    layout = [[sg.Column(layout1, key='-COL1-'), sg.Column(layout2, visible=False, key='-COL2-')]]


    # Create the Window
    window = sg.Window('The FuckYouTimesheets Program', layout)

    layout = 1  # The currently visible layout
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit'):
            break
        if event == 'Ok':
            getToken()


            window[f'-COL{layout}-'].update(visible=False)
            layout = layout + 1 if layout < 2 else 1
            window[f'-COL{layout}-'].update(visible=True)



    window.close()

# calls the node cli.js process to go do the oauth2 code flow and get back the access token from it
def getToken():
    result = subprocess.run(['node', 'cli.js'], capture_output=True)
    access_token = result.stdout.decode()
    print(access_token)

main()
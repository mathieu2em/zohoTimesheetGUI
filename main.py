import PySimpleGUI as sg
import sys  # For simplicity, we'll read config file from 1st CLI param sys.argv[1]
import json
import subprocess
import urllib
import requests
import webbrowser
import os
from datetime import date

sg.theme('DarkBlue16')   # Add a touch of color.

def main():
    global config
    global access_token
    global user_id
    global task_id 
    global project_id

    FONT_BIG = 'Any 12'
    FONT = 'Any 10'
    FONT_NUM = 'Helvetica 12'

    config = json.load(open(resource_path("credentials.json")))

    today = date.today().strftime("%Y-%m-%d").split('-')

    # ----------- Create the 2 layouts this Window will display. -----------

    # The first page for acquiring the token.
    layout1 = [[sg.Text('First, you have to get a token from zoho', font=FONT_BIG)],
                [sg.Button('Ok', key='lay-1-ok-btn', font=FONT_BIG), sg.Button('Exit', font=FONT_BIG)]]

    # The second page for creating the timesheet.
    layout2 = [ [sg.Text('Enter the tasks you did today.', font=FONT_BIG)],
                [sg.Multiline('', size=(110,5))],
                # Task choosing menu 
                # TODO : there is a BETTER way to do it and I know it.
                [sg.Text('Click on the corresponding task:', font=FONT_BIG)],
                # SPECTRA - TASKS
                [sg.Text('SpectrA: ', font=FONT), 
                 sg.Button('Programmation - Capitalisable',       key='sp-1', font=FONT),
                 sg.Button('Analyse - Capitalisable',             key='sp-2', font=FONT),
                 sg.Button('Rencontre',                           key='sp-3', font=FONT),
                 sg.Button('Soutien Technique Interne',           key='sp-4', font=FONT),
                 sg.Button('Controle de qualité - Capitalisable', key='sp-5', font=FONT)
                 ],
                # ADMIN TASKS
                [sg.Text('Administration: ', font=FONT),
                 sg.Button('Administration - Générale', key='ad-1', font=FONT),
                 sg.Button('Jour férié',                key='ad-2', font=FONT),
                 sg.Button('Absence pour maladie',      key='ad-3', font=FONT),
                 sg.Button('Vacances',                  key='ad-4', font=FONT)
                 ],
                # EDILEXPERT TASKS
                [sg.Text('Edilexpert', font=FONT), 
                sg.Button('Analyse',       key='ex-1', font=FONT), 
                sg.Button('Programmation', key='ex-2', font=FONT)],
                # TIME OPTIONS
                [sg.Text('Date of the timesheet : aaaa-mm-dd', font=FONT_BIG), sg.InputText(today[0], size=(4,1), font=FONT_NUM), sg.InputText(today[1], size=(2,1), font=FONT_NUM), sg.InputText(today[2], size=(2,1), font=FONT_NUM)],
                [sg.Text('How much time did you do this task ? (Default 07:30)', font=FONT_BIG), sg.InputText('07:30', size=(5,4), font=FONT_NUM)],
                # MISC
                [sg.Checkbox('Is billable', default=False, font=FONT_BIG)],

                [sg.Button('Create timesheet', font=FONT_BIG), sg.Button('Go to your zoho timesheets', font=FONT_BIG), sg.Button('Exit', font=FONT_BIG)]]

    # ----------- Create actual layout using Columns.
    layout = [[sg.Column(layout1, key='-COL1-'), sg.Column(layout2, visible=False, key='-COL2-')]]


    # Create the Window.
    window = sg.Window('Zoho Timesheet GUI', layout, icon=resource_path('logo.ico'), grab_anywhere=True)

    layout = 1  # The currently visible layout.
    # Event Loop to process "events" and get the "values" of the inputs.
    while True:
        event, values = window.read()
        # For test purpose.
        print(event, values)
        # The exit0 is needed as pysimplegui gives a different name for the layout2 exit button. (adds 0 at the end)
        if event in (None, 'Exit', 'Exit0'):
            break
        # Get the access token.
        elif event == 'lay-1-ok-btn':
            # Call a node js executable.
            access_token = getToken()
            # Needed for api call for timesheet creation.
            user_id = getCurrentUser(access_token)

            # This is part of the logic making the first page (layout 1) invisible. And second page ( layout 2 ) visible.
            window[f'-COL{layout}-'].update(visible=False)
            layout = layout + 1 if layout < 2 else 1
            window[f'-COL{layout}-'].update(visible=True)

        # The buttons for the task, use the task ID that I manually entered in credentials.
        # todo : Make this part automatic from api call to available tasks ?
        elif 'sp-' in event:
            project_id = config['project_id_spectra']
            task_id = task_assign(event)
        elif 'ex-' in event:
            project_id = config['project_id_edilexpert']
            task_id = task_assign(event)
        elif 'ad-' in event:
            project_id = config['project_id_administration']
            task_id = task_assign(event)
        elif 'Go to your zoho timesheets':
            webbrowser.open('https://books.zoho.com/app#/timesheet/alltimeentries?filter_by=Status.All%2CDate.ThisMonth&per_page=25&sort_column=task_name&sort_order=A', new=2)
        # The timesheet creation event being triggered, we extract infos to send with api call.
        elif event == 'Create timesheet':
            
            # Conditional on selection of which task to send to which project by user.
            if not task_id:
                sg.popup_ok('YOU MUST SELECT A TASK BEFORE SENDING SHEET')
            else:
                note = values[0]
                # How much time the user executed his task.
                log_time = values[4]
                # Date formatting YYYY-MM-DD
                taskdate = values[1] + '-' + values[2] + '-' + values[3]
                # A boolean value.
                billable = values[5]
                # A little loop for error handling in case token is expired.
                responseSuccess = False
                while not responseSuccess:
                    response = produceTimesheet(project_id, user_id, task_id, access_token, log_time, taskdate, billable, note)
                    print(response)
                    if response["code"] == 0:
                        sg.popup_ok('your timesheet has been successfully created !')
                        responseSuccess = True
                    elif response["code"] == 401:
                        sg.popup_ok('the authentication expired (currently takes 1 hour to expire) click ok to get another one.')
                        access_token = getToken()
                    else:
                        sg.popup_ok(response['message'])
                        # Not a success but get out of the loop anyway.
                        responseSuccess = True
                

    window.close()

# Assign the correct task_id dependent on button id pressed.
def task_assign(taskButtonID):
    switcher = {
        'sp-1': config['task_sp_prog_cap'],
        'sp-2': config['task_sp_anal_cap'],
        'sp-3': config['task_sp_rencontre'],
        'sp-4': config['task_sp_sout_tec'],
        'sp-5': config['task_sp_QA_cap'],

        'ad-1': config['task_admin_general'],
        'ad-2': config['task_admin_jourferie'],
        'ad-3': config['task_admin_maladie'],
        'ad-4': config['task_admin_vacances'],

        'ex-1': config['task_ex_anal'],
        'ex-2': config['task_ex_prog']
    }
    result = switcher.get(taskButtonID, "TASK NOT FOUND")
    print(result)
    return result

# Needed because of a bug with pyinstaller file path when using --add-data on windows
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Needed because that we have to read from stdout but we do not want a visible console to the user as it is ugly.
# found this solution deep deep deep in the web. Not sure of the usefullness of the startupinfo part. TODO to investigate
def popen(cmd: str) -> str:
    # Process are not working the same on linux
    if not sys.platform.startswith('linux'):
        # For pyinstaller -w
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Tell std*s to use PIPE as the links must be created.
        process = subprocess.Popen(cmd,startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    else:
        # Tell std*s to use PIPE as the links must be created.
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    return process.stdout.read()

# calls the node cli.js process to go do the oauth2 code flow and get back the access token from it
def getToken():
    # to decide which node process package we need to use
    if sys.platform.startswith('linux'):
        nodeProcessFile = './zohotimesheetgui-linux'
    elif sys.platform.startswith('win32'):
        nodeProcessFile = 'zohotimesheetgui-win.exe'
    elif sys.platform.startswith('darwin'):
        nodeProcessFile = 'zohotimesheetgui-macos'
    
    result = popen(resource_path(nodeProcessFile))
    # as it is byte encoded, decode it.
    access_token = result.decode()
    print(access_token)
    return access_token

# Calls zoho api with access token to get current user id.
def getCurrentUser(access_token):
    url = "https://books.zoho.com/api/v3/users/me"

    payload={}
    headers = {
    'Authorization': 'Zoho-oauthtoken ' + access_token
    }

    response = requests.request("GET", url, headers=headers, data=payload).json()
    userID = response['user']["user_id"]
    print(userID)
    return userID

# Sends an api request to zoho in order to create a timesheet.
def produceTimesheet(project_id, user_id, task_id, access_token, log_time, date, billable, note):
    print('produceTimesheetMethodCalled')
    url = "https://books.zoho.com/api/v3/projects/timeentries?organization_id=" + config["org_id"]

    payload={'JSONString':json.dumps({
        # TODO : should set it up so the user can choose between projects
        'project_id': project_id,
        'task_id': task_id,
        'user_id': user_id,
        'log_date': date,
        'log_time': log_time,
        'is_billable': billable,
        'notes': note})}

    headers = {
        'Authorization': 'Zoho-oauthtoken ' + access_token,
        'Content-Type': 'application/x-www-form-urlencoded'
        }

    response = requests.post( url, data=urllib.parse.urlencode(payload), headers=headers)

    return response.json()

main()
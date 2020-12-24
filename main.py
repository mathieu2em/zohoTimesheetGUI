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
    config = json.load(open(resource_path("credentials.json")))

    task_id = config['task_prog_cap']
    today = date.today().strftime("%Y-%m-%d").split('-')

    # ----------- Create the 3 layouts this Window will display. -----------
    layout1 = [[sg.Text('First, you have to get a token from zoho')],
                [sg.Button('Ok'), sg.Button('Exit')]]

    layout2 = [ [sg.Text('Enter the tasks you did today.')],
                [sg.Multiline('', size=(110,5))],
                [sg.Text('Click on the corresponding task:'), sg.Button('Programmation - Capitalisable'), sg.Button('Analyse - Capitalisable'), sg.Button('Rencontre'), sg.Button('Soutien Technique Interne')],
                [sg.Text('Date of the timesheet : aaaa-mm-dd'), sg.InputText(today[0], size=(4,1)), sg.InputText(today[1], size=(2,1)), sg.InputText(today[2], size=(2,1))],
                [sg.Text('How much time did you do this task ? (Default 07:30)'), sg.InputText('07:30', size=(5,4))],
                [sg.Checkbox('Is billable', default=False)],
                [sg.Button('Create timesheet')]]

    # ----------- Create actual layout using Columns and a row of Buttons.
    layout = [[sg.Column(layout1, key='-COL1-'), sg.Column(layout2, visible=False, key='-COL2-')]]


    # Create the Window.
    window = sg.Window('Zoho Timesheet GUI', layout)

    layout = 1  # The currently visible layout.
    # Event Loop to process "events" and get the "values" of the inputs.
    while True:
        event, values = window.read()
        # For test purpose.
        # print(event, values)
        if event in (None, 'Exit'):
            break
        # Get the access token.
        if event == 'Ok':
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
        if event == 'Programmation - Capitalisable':
            task_id = config['task_prog_cap']
        if event == 'Analyse - Capitalisable':
            task_id = config['task_anal_cap']
        if event == 'Rencontre':
            task_id = config['task_rencontre']
        if event == 'Soutien Technique Interne':
            task_id = config['task_sout_int']
        # The timesheet creation event being triggered, we extract infos to send with api call.
        if event == 'Create timesheet':
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
                response = produceTimesheet(user_id, task_id, access_token, log_time, taskdate, billable, note)
                if response["code"] == 0:
                    sg.popup_ok('your timesheet has been successfully created !')
                    responseSuccess = True
                elif response["code"] == 401:
                    sg.popup_ok('the authentication expired (currently takes 1 hour to expire) click ok to get another one.')
                    access_token = getToken()
                else:
                    # Not a success but get out of the loop anyway.
                    responseSuccess = True
                

    window.close()

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
    return access_token

# Calls zoho api with access token to get current user id.
def getCurrentUser(access_token):
    url = "https://books.zoho.com/api/v3/users/me"

    payload={}
    headers = {
    'Authorization': 'Zoho-oauthtoken ' + access_token,
    'Cookie': 'BuildCookie_669075739=1; stk=567c8fc659f3915622145aeb7c09a64d; ba05f91d88=2d12156dff1cddc63ec0fafe285ed2a4; zbcscook=11de33d1-3853-44c4-9dff-364cddc40635; _zcsr_tmp=11de33d1-3853-44c4-9dff-364cddc40635; ZohoBooksRef=https://books.zoho.com/oauth/v2/token?grant_type=authorization_code&client_id=1000.SXN2Y98RNA1M3N3OPI95GQ3VVFX8OX&client_secret=582d2cdb0e4bb366068b997b375f62d6217df28aa4&redirect_uri=https://google.com&code=1000.89a071e6726751d5eb427f4562ac92e0.b41c46b41df2da07ac273fce1be3e9f1; ZohoBooksPageURL=https://books.zoho.com/; JSESSIONID=00C99E0DC1A658F3567A57367C62E97C'
    }

    response = requests.request("GET", url, headers=headers, data=payload).json()
    userID = response['user']["user_id"]

    return userID

def produceTimesheet(userID, task_id, access_token, log_time, date, billable, note):

    url = "https://books.zoho.com/api/v3/projects/timeentries?organization_id=669075739"

    payload={'JSONString':json.dumps({
        'project_id': '1408740000003723131',
        'task_id': task_id,
        'user_id': userID,
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
import PySimpleGUI as sg
import sys  # For simplicity, we'll read config file from 1st CLI param sys.argv[1]
import json
import logging
import subprocess
import urllib
import requests
import time
import webbrowser
from datetime import date

sg.theme('DarkAmber')   # Add a touch of color



def main():
    global config
    global access_token
    global user_id
    global task_id 
    config = json.load(open("credentials.json"))

    task_id = config['task_prog_cap']
    today = date.today().strftime("%Y-%m-%d").split('-')

    # ----------- Create the 3 layouts this Window will display -----------
    layout1 = [[sg.Text('First, you have to get a token from zoho')],
                [sg.Button('Ok'), sg.Button('Exit')]]

    layout2 = [
                [sg.Multiline('enter the tasks you did today', size=(100,5))],
                [sg.Text('click on the corresponding task'), sg.Button('Programmation - Capitalisable'), sg.Button('Analyse - Capitalisable'), sg.Button('Rencontre'), sg.Button('Soutien Technique Interne')],
                [sg.Text('Date of the timesheet : aaaa-mm-dd'), sg.InputText(today[0], size=(4,1)), sg.InputText(today[1], size=(2,1)), sg.InputText(today[2], size=(2,1))],
                [sg.Text('how much time did you work ? (default 07:30)'), sg.InputText('07:30', size=(5,4))],
                [sg.Checkbox('is billable', default=False)],
                [sg.Button('Create today timesheet')]]

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
        # routine de retrait du access token
        if event == 'Ok':
            access_token = getToken()
            user_id = getCurrentUser(access_token)

            window[f'-COL{layout}-'].update(visible=False)
            layout = layout + 1 if layout < 2 else 1
            window[f'-COL{layout}-'].update(visible=True)
        if event == 'Programmation - Capitalisable':
            task_id = config['task_prog_cap']
        if event == 'Analyse - Capitalisable':
            task_id = config['task_anal_cap']
        if event == 'Rencontre':
            task_id = config['task_rencontre']
        if event == 'Soutien Technique Interne':
            task_id = config['task_sout_int']
        if event == 'Create today timesheet':
            note = values[0]
            log_time = values[4]
            taskdate = values[1] + '-' + values[2] + '-' + values[3]
            billable = values[5]
            response = produceTimesheet(user_id, task_id, access_token, log_time, taskdate, billable, note)
            if response["code"] == 0:
                sg.popup_ok('your timesheet has been successfully created !')
            else:
                sg.popup_ok('something went wrong (maybe the time format ? should be 00:00) ')

    window.close()

# calls the node cli.js process to go do the oauth2 code flow and get back the access token from it
def getToken():
    result = subprocess.run(['node', 'cli.js'], capture_output=True)
    access_token = result.stdout.decode()
    print(access_token)
    return access_token

# calls zoho api with access token to get current user id
def getCurrentUser(access_token):
    url = "https://books.zoho.com/api/v3/users/me"

    payload={}
    headers = {
    'Authorization': 'Zoho-oauthtoken ' + access_token,
    'Cookie': 'BuildCookie_669075739=1; stk=567c8fc659f3915622145aeb7c09a64d; ba05f91d88=2d12156dff1cddc63ec0fafe285ed2a4; zbcscook=11de33d1-3853-44c4-9dff-364cddc40635; _zcsr_tmp=11de33d1-3853-44c4-9dff-364cddc40635; ZohoBooksRef=https://books.zoho.com/oauth/v2/token?grant_type=authorization_code&client_id=1000.SXN2Y98RNA1M3N3OPI95GQ3VVFX8OX&client_secret=582d2cdb0e4bb366068b997b375f62d6217df28aa4&redirect_uri=https://google.com&code=1000.89a071e6726751d5eb427f4562ac92e0.b41c46b41df2da07ac273fce1be3e9f1; ZohoBooksPageURL=https://books.zoho.com/; JSESSIONID=00C99E0DC1A658F3567A57367C62E97C'
    }

    response = requests.request("GET", url, headers=headers, data=payload).json()
    userID = response['user']["user_id"]
    print(userID)
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

    print(response.text)
    return response.json()


main()
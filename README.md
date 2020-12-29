# zohoTimesheetGUI
an app to enter a day timemesheet task with comment in Zoho books timesheet directly from your pc!

![image](https://user-images.githubusercontent.com/35858630/103262070-d0507d00-4971-11eb-88d2-7a8577419190.png)

![timesheets3](https://user-images.githubusercontent.com/35858630/103262901-435af300-4974-11eb-82ae-b24e72c09095.gif)

# how to use.

you need to install node js and python3

then run these commands

for node :
npm install open

for python3 :
pip install -r requirements.txt

now if you are not from my organisation , [follow the cli.js setup from their basic repo](https://github.com/taskanalytics/ta-zoho)

( you have to add the correct client_id and client_secret from your Zoho developper console account into cli.js for node to identify you to the correct place.
then you have ton enter in credentials the org_id : your organisation id , the tasks id of the tasks you want to offer as options, etc. )

# to compile a exe file 

install pyinstaller using this command : pip install pyinstaller

now use this command : pyinstaller --onefile --add-data "zohotimesheetgui-win.exe;." --add-data "credentials.json;." --noconsole --clean .\main.py  


a special thanks for the cli.js base code that I modified from this repository : https://github.com/taskanalytics/ta-zoho from [@taskanalytics]( https://github.com/taskanalytics )

Python now runs a subprocess calling cli.js for the oauth2.0 authentication part. It then has the necessary access_token to do its job

TODO:
[ ] add the refresh token and refresh logic to python code


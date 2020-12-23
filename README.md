# zohoTimesheetGUI
an app to enter a day time with comment in Zoho books timesheet directly from your pc!

![timesheets2](https://user-images.githubusercontent.com/35858630/103024338-9f112080-451d-11eb-9d90-5019b88bb5c9.gif)

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

a special thanks for the cli.js base code that I modified from this repository : https://github.com/taskanalytics/ta-zoho from [@taskanalytics]( https://github.com/taskanalytics )

Python now runs a subprocess calling cli.js for the oauth2.0 authentication part. It then has the necessary access_token to do its job

TODO:
[ ] add the refresh token and refresh logic to python code
